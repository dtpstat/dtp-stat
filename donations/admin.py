from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from .constants import SUBSCRIPTION_THRESHOLD_DAYS
from .models import Contact, Currency, CurrencyPriceHistory, Donation, Goal, Level, Subscription


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """
    Admin interface for the Level model.
    Levels define subscription tiers like "Bronze", "Silver", "Gold".
    """
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),  # Make this section collapsible
        }),
    )


class SubscriptionInline(admin.TabularInline):
    """
    Inline for displaying a Contact's Subscriptions on the Contact admin page.
    Using TabularInline for a more compact view.
    """
    model = Subscription
    extra = 0  # Don't show extra empty forms by default
    show_change_link = True  # Allow easy navigation to the subscription's change page
    fields = ('level', 'amount', 'currency', 'frequency', 'start_date')
    readonly_fields = ('created_at', 'updated_at')


class DonationInline(admin.TabularInline):
    """
    Inline for displaying Donations on Contact and Subscription admin pages.
    """
    model = Donation
    extra = 0
    show_change_link = True
    fields = ('donation_datetime', 'amount', 'currency', 'is_confirmed', 'source')
    # Use raw_id_fields for ForeignKey to avoid performance issues with large datasets
    raw_id_fields = ('contact', 'subscription')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface for the Contact model.
    Includes inlines for related Subscriptions and Donations for a holistic view.
    """
    list_display = ('__str__', 'email', 'telegram', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email', 'telegram', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SubscriptionInline, DonationInline]

    fieldsets = (
        (_('Contact Information'), {
            'fields': ('email', 'telegram', 'phone')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """
    Admin interface for the Goal model.
    Goals represent fundraising targets.
    """
    list_display = ('__str__', 'target_amount', 'current_amount_raised', 'proposal_contribution', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('target_amount',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-start_date',)

    fieldsets = (
        (None, {
            'fields': ('target_amount', 'start_date', 'end_date')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class SubscriptionWithoutDonationFilter(admin.SimpleListFilter):
    title = _('Without expected donation')
    parameter_name = 'without_expected_donation'

    def lookups(self, request, model_admin):
        return (
            ('true', _('Show')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.model.objects.with_overdue_donations(queryset)
        return queryset


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Admin interface for the Subscription model.
    Manages recurring donations.
    """
    list_display = (
        'id',
        'contact',
        'level',
        'frequency',
        'is_active',
        'start_date',
        'end_date',
        'last_expected_date',
        'days_since_last_expected',
        'check_button',
        'disable_button',
    )
    list_filter = (SubscriptionWithoutDonationFilter, 'frequency', 'level', 'currency', 'start_date')
    search_fields = ('contact__email', 'contact__telegram', 'source', 'amount')
    # Use raw_id_fields for ForeignKey to avoid performance issues with large datasets
    raw_id_fields = ('contact',)
    readonly_fields = ('created_at', 'updated_at', 'is_active', 'payment_dates_table', 'disable_button', 'check_button')
    inlines = [DonationInline]

    fieldsets = (
        (_('Actions'), {
            'fields': ('check_button', 'disable_button',)
        }),
        (_('Core Information'), {
            'fields': ('contact', 'level')
        }),
        (_('Payment Details'), {
            'fields': ('amount', 'currency', 'frequency', 'source')
        }),
        (_('Timeline'), {
            'fields': ('start_date', 'end_date', 'is_active', 'payment_dates_table')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def is_active(self, obj):
        return obj.is_active

    def payment_dates_table(self, obj):
        payment_dates = obj.get_payment_dates()
        today = timezone.now().date()
        rows = ["<tr><th>Payment Date</th><th>Donation</th></tr>"]
        donations = list(Donation.objects.find_donations_by_contact_amount_currency_and_dates(
            contact=obj.contact,
            amount=obj.amount,
            currency=obj.currency,
            dates=payment_dates,
            threshold=0,
        ))
        for i, payment_date in enumerate(payment_dates):
            if i < len(donations):
                href = reverse(f'admin:donations_donation_change', args=[donations[i].id])
                link = f'<a href="{href}">{donations[i]}</a>'
            else:
                link = ''
            rows.append(f"<tr><td>{payment_date}</td><td>{link}</td></tr>")
            if payment_date > today:
                break
        return mark_safe(f"<table>{''.join(rows)}</table>")

    def get_urls(self):
        """
        Add a custom URL for our disable action.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/disable/',
                self.admin_site.admin_view(self.process_disable),
                name='subscription_disable',  # Use a unique name
            ),
            path(
                '<path:object_id>/check/',
                self.admin_site.admin_view(self.process_check),
                name='subscription_check',  # Use a unique name
            ),
        ]
        return custom_urls + urls

    def process_check(self, request, object_id, *args, **kwargs):
        """
        The view that handles the check action.
        """
        subscription = self.get_object(request, object_id)

        if subscription:
            # Call the model's method
            is_active = subscription.check_donation()
            # Add a success message
            if is_active:
                self.message_user(request, _("Subscription has been successfully checked."), messages.SUCCESS)
            else:
                self.message_user(request, _("Subscription has been disabled."), messages.SUCCESS)

        # Redirect back to the changelist view
        url = reverse(
            'admin:%s_%s_changelist' % (
                self.opts.app_label, self.opts.model_name
            )
        )
        return HttpResponseRedirect(url)


    def process_disable(self, request, object_id, *args, **kwargs):
        """
        The view that handles the disable action.
        """
        subscription = self.get_object(request, object_id)

        if subscription:
            subscription.disable()
            self.message_user(request, _("Subscription has been successfully disabled."), messages.SUCCESS)

        url = reverse(
            'admin:%s_%s_changelist' % (
                self.opts.app_label, self.opts.model_name
            )
        )
        return HttpResponseRedirect(url)

    def disable_button(self, obj):
        """
        Render the button in the admin form.
        """
        if obj.is_active:
            url = reverse('admin:subscription_disable', args=[obj.pk])
            return format_html(
                '<a class="button deletelink" href="{}">{}</a>',
                url,
                _('Disable Now')
            )
        return _("This subscription is already disabled.")
    disable_button.short_description = _("Disable Subscription")

    def check_button(self, obj):
        """
        Render the button in the admin form.
        """
        if obj.is_active:
            url = reverse('admin:subscription_check', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}">{}</a>',
                url,
                _('Check Now')
            )
        return _("This subscription is already disabled.")
    check_button.short_description = _("Check Subscription")

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """
    Admin interface for the Donation model.
    Manages individual donation records.
    """
    list_display = ('id', 'donation_datetime', 'contact', 'amount_with_currency', 'is_confirmed', 'subscription')
    list_filter = ('is_confirmed', 'donation_datetime', 'currency', 'source')
    search_fields = ('contact__email', 'contact__telegram', 'source', 'amount')
    # Use raw_id_fields for ForeignKeys to avoid performance issues with large datasets
    raw_id_fields = ('contact', 'subscription')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Association'), {
            'description': _("Link this donation to a contact and, optionally, a subscription."),
            'fields': ('contact', 'subscription')
        }),
        (_('Payment Information'), {
            'fields': ('amount', 'currency', 'amount_in_base_currency', 'is_confirmed')
        }),
        (_('Metadata'), {
            'fields': ('donation_datetime', 'source')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # @admin.display(description=_('Amount'), ordering='amount')
    def amount_with_currency(self, obj):
        """
        Custom method to display amount and currency together in the list view.
        """
        return f"{obj.amount} {obj.currency}"


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'latest_price', 'created_at', 'updated_at')

@admin.register(CurrencyPriceHistory)
class CurrencyPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('currency', 'price', 'datetime')