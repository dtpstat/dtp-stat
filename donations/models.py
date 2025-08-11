from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from dateutil.rrule import rrule, WEEKLY, MONTHLY
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from donations.constants import SUBSCRIPTION_THRESHOLD_DAYS
from donations.managers import CurrencyPriceHistoryManager, DonationManager, GoalManager, SubscriptionManager


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating
    `created_at` and `updated_at` fields.
    """
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
        help_text=_("The date and time this object was first created.")
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
        help_text=_("The date and time this object was last updated.")
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Level(TimeStampedModel):
    """
    Defines different tiers for subscriptions (e.g., "Bronze", "Silver", "Gold").
    """
    name = models.CharField(
        _("name"),
        max_length=100,
        unique=True,
        help_text=_("The unique name of the subscription level.")
    )
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("A description of the benefits for this level.")
    )

    class Meta:
        verbose_name = _("Level")
        verbose_name_plural = _("Levels")
        ordering = ['name']

    def __str__(self):
        return self.name


class Contact(TimeStampedModel):
    """
    Represents an individual donor or contact.
    """
    class Status(models.TextChoices):
        ACTIVE = 'Active', _('Active')
        ARCHIVED = 'Archived', _('Archived')
        DO_NOT_CONTACT = 'Do Not Contact', _('Do Not Contact')

    email = models.EmailField(
        _("email address"),
        unique=True,
        null=True,
        blank=True,
        help_text=_("The primary email address of the contact. Must be unique.")
    )
    telegram = models.CharField(
        _("telegram handle"),
        max_length=100,
        blank=True,
        help_text=_("The contact's Telegram username.")
    )
    phone = models.CharField(
        _("phone number"),
        max_length=20,
        blank=True,
        help_text=_("The contact's phone number.")
    )
    status = models.CharField(
        _("status"),
        max_length=50,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text=_("The current status of the contact.")
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __str__(self):
        return f"Contact {self.pk}"

    def clean(self):
        """
        Ensures that at least one method of contact is provided.
        """
        super().clean()
        if not self.email and not self.telegram and not self.phone:
            raise ValidationError(
                _("A contact must have at least an email, a telegram handle, or a phone number.")
            )


class Goal(TimeStampedModel):
    """
    Defines a fundraising goal with a target amount and date range.
    """
    target_amount = models.DecimalField(
        _("target amount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("The target amount to be raised for this goal. Must be positive.")
    )
    start_date = models.DateField(
        _("start date"),
        help_text=_("The start date of the fundraising period.")
    )
    end_date = models.DateField(
        _("end date"),
        help_text=_("The end date of the fundraising period.")
    )
    objects = GoalManager()

    class Meta:
        verbose_name = _("Goal")
        verbose_name_plural = _("Goals")
        ordering = ['-start_date']

    def __str__(self):
        return _("Goal: %(start_date)s to %(end_date)s") % {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

    def clean(self):
        """
        Ensures the end date is not before the start date.
        """
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(_("The end date cannot be before the start date."))

    @property
    def current_amount_raised(self):
        """Calculates the sum of confirmed donations within the goal's date range."""
        total = Donation.objects.total_donated_in_range(self.start_date, self.end_date)
        return total

    @property
    def proposal_contribution(self):
        """Calculates the proposal contribution for the goal."""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        subscriptions = Subscription.objects.active_subscriptions()
        total = 0
        for subscription in subscriptions:
            total += subscription.calculate_proposal_contribution_in_range(
                start_date=max(today, self.start_date),
                end_date=self.end_date,
            )
        return total

    @property
    def days_until_end(self):
        """Calculates the number of days until the goal's end date."""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days

class Subscription(TimeStampedModel):
    """
    Represents a recurring donation (subscription) from a contact.
    """
    class Frequency(models.TextChoices):
        WEEKLY = 'weekly', _('Weekly')
        MONTHLY = 'monthly', _('Monthly')

    contact = models.ForeignKey(
        'Contact',
        on_delete=models.PROTECT,
        verbose_name=_("contact"),
        help_text=_("The contact who owns this subscription."),
        related_name="subscriptions"
    )
    level = models.ForeignKey(
        'Level',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("level"),
        help_text=_("The subscription level. Becomes null if the level is deleted."),
        related_name="subscriptions"
    )
    amount = models.DecimalField(
        _("amount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("The amount for each recurring donation. Must be positive.")
    )
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        verbose_name=_("currency"),
        help_text=_("The currency of the subscription (e.g., USD, EUR).")
    )
    start_date = models.DateField(
        _("start date"),
        help_text=_("The date the first payment is due or was made.")
    )
    frequency = models.CharField(
        _("frequency"),
        max_length=50,
        choices=Frequency.choices,
        help_text=_("How often the donation recurs.")
    )
    end_date = models.DateField(
        _("subscription end date"),
        null=True,
        blank=True,
        help_text=_("The date this subscription is scheduled to end, if any.")
    )
    source = models.CharField(
        _("source"),
        max_length=255,
        blank=True,
        help_text=_("Notes on where this subscription originated from (e.g., 'Patreon', 'Stripe').")
    )
    objects = SubscriptionManager()

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def __str__(self):
        return _("%(amount)s %(currency)s/%(frequency)s by %(contact)s") % {
            'amount': self.amount,
            'currency': self.currency,
            'frequency': self.get_frequency_display(),
            'contact': self.contact
        }

    def clean(self):
        """
        Validates that the end date is not before the start date.
        """
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(_("The subscription end date cannot be before the start date."))

    @property
    def is_active(self):
        """Returns True if the subscription is active."""
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        else:
            return self.start_date <= today

    def get_payment_dates(self, *, start_date: Optional[date] = None, end_date: Optional[date] = None) -> list:
        rule_freq = WEEKLY if self.frequency == self.Frequency.WEEKLY else MONTHLY
        if not end_date:
            end_date = timezone.now().date() + timedelta(days=365)
        effective_until_date = end_date
        if self.end_date:
            effective_until_date = self.end_date
        if end_date and self.end_date:
            effective_until_date = min(effective_until_date, end_date)

        payment_dates = list(rrule(
            freq=rule_freq,
            dtstart=self.start_date,
            until=effective_until_date
        ))

        if start_date:
            payment_dates = filter(lambda x: x.date() >= start_date, payment_dates)

        return [payment_date.date() for payment_date in payment_dates]

    def calculate_proposal_contribution_in_range(
            self, *,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None):
        _start_date = max(start_date, self.start_date) if start_date else self.start_date
        if not end_date:
            end_date = timezone.now().date() + timedelta(days=365)
        _end_date = min(end_date, self.end_date) if self.end_date else end_date
        payment_dates = self.get_payment_dates(start_date=_start_date, end_date=_end_date)
        total = self.amount * len(payment_dates)
        currency_price = self.currency.latest_price or 0
        return total * currency_price

    def disable(self, on_date: Optional[date] = None):
        if not on_date:
            on_date = timezone.now().date()
        self.end_date = on_date
        self.save(update_fields=['end_date', 'updated_at'])

    def check_donation(self, on_date: Optional[date] = None, disable = True, threshold: Optional[int] = None):
        if threshold is None:
            threshold = SUBSCRIPTION_THRESHOLD_DAYS
        if not on_date:
            on_date = timezone.now().date() - timedelta(days=threshold)
        payment_dates = self.get_payment_dates(
            end_date=on_date,
        )
        last_payment_date = payment_dates[-1] if payment_dates else None
        if not last_payment_date:
            return True
        if not Donation.objects.find_donations_by_contact_amount_currency_and_dates(
            contact=self.contact,
            amount=self.amount,
            currency=self.currency,
            dates=[last_payment_date],
            threshold=threshold,
        ).exists():
            if disable:
                self.disable(on_date=last_payment_date)
            return False
        return True

class Donation(TimeStampedModel):
    """
    Represents a single, one-off donation or an instance of a recurring subscription payment.
    """
    contact = models.ForeignKey(
        'Contact',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("contact"),
        help_text=_("The contact who made the donation. Can be empty for anonymous donations."),
        related_name="donations"
    )
    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("subscription"),
        help_text=_("The subscription this donation is a part of. Empty for one-off donations."),
        related_name="donations"
    )
    amount = models.DecimalField(
        _("amount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("The amount donated in its original currency. Must be positive.")
    )
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        verbose_name=_("currency"),
        help_text=_("The currency of the donation (e.g., USD, EUR).")
    )
    amount_in_base_currency = models.DecimalField(
        _("amount in base currency"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True,
        blank=True,
        help_text=_("The donated amount converted to the base currency. Required when the donation is confirmed.")
    )
    donation_datetime = models.DateTimeField(
        _("donation date and time"),
        default=timezone.now,
        help_text=_("When the donation was received.")
    )
    source = models.CharField(
        _("source"),
        max_length=255,
        blank=True,
        help_text=_("Notes on where this donation came from (e.g., 'Bank Transfer', 'Website Form').")
    )
    is_confirmed = models.BooleanField(
        _("is confirmed"),
        default=False,
        help_text=_("Designates whether this donation has been confirmed and processed.")
    )
    objects = DonationManager()

    class Meta:
        verbose_name = _("Donation")
        verbose_name_plural = _("Donations")
        ordering = ['-donation_datetime']

    def __str__(self):
        return _("%(amount)s %(currency)s on %(date)s (%(confirmed)s)") % {
            'amount': self.amount,
            'currency': self.currency.code,
            'date': self.donation_datetime.strftime('%Y-%m-%d'),
            'confirmed': _('Confirmed') if self.is_confirmed else _('Unconfirmed'),
        }

    def clean(self):
        """
        Validates the donation's integrity:
        1. If linked to a subscription, the contact must match the subscription's contact.
        2. If anonymous (no contact), it cannot be linked to a subscription.
        3. If the donation is confirmed, the amount in base currency must be set.
        """
        super().clean()
        if self.subscription:
            if not self.contact:
                raise ValidationError(
                    _("A donation linked to a subscription must also be linked to a contact.")
                )
            if self.contact != self.subscription.contact:
                raise ValidationError(
                    _("The contact for this donation does not match the contact on the subscription.")
                )
        
        if self.is_confirmed and self.amount_in_base_currency is None:
            raise ValidationError({
                'amount_in_base_currency': _('This field is required for confirmed donations.')
            })

class Currency(TimeStampedModel):
    """Represents a currency used for donations and subscriptions."""
    name = models.CharField(
        verbose_name=_("name"),
        max_length=100,
        unique=True,
        help_text=_("The unique name of the currency (e.g., 'US Dollar', 'Euro').")
    )
    code = models.CharField(
        verbose_name=_("code"),
        max_length=10,
        help_text=_("The currency code (e.g., 'USD', 'EUR')."),
        unique=True,
    )

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
        ordering = ['code']

    def __str__(self):
        return f"({self.code}) {self.name}"

    @property
    def latest_price(self) -> Optional[Decimal]:
        """Returns the latest price of the currency."""
        history_price = CurrencyPriceHistory.objects.get_latest_price(currency=self)
        return history_price.price if history_price else None


class CurrencyPriceHistory(TimeStampedModel):
    """Represents a historical price of a currency."""
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.CASCADE,
        verbose_name=_("Currency"),
        help_text=_("The currency for which this price is valid.")
    )
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("The price of the currency in the base currency.")
    )
    datetime = models.DateTimeField(
        _("datetime"),
        help_text=_("The date and time this price was recorded.")
    )

    objects = CurrencyPriceHistoryManager()

    class Meta:
        verbose_name = _("Currency Price History")
        verbose_name_plural = _("Currency Price Histories")
        ordering = ['-datetime']

    def __str__(self):
        return f"{self.currency.code} {self.datetime}"