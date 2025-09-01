from django.db import models
from django.db.models import Q, Case, When
from django.utils import timezone


class SubscriptionManager(models.Manager):
    def active_subscriptions(self):
        """Returns a queryset of all active subscriptions."""
        today = timezone.now().date()

        return self.get_queryset().filter(
            start_date__lte=today,
        ).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True),
        )

    def with_overdue_donations(self, queryset = None):
        from ..models import Donation

        if queryset is None:
            queryset = self.get_queryset()

        today = timezone.now().date()
        overdue_subs_data = []

        for sub in self.active_subscriptions():
            payment_dates = sub.get_payment_dates()
            expected_dates_in_past = [d for d in payment_dates if d <= today]

            if not expected_dates_in_past:
                continue

            last_expected_date = expected_dates_in_past[-1]
            days_since_last_expected = (today - last_expected_date).days

            if days_since_last_expected > 0:
                donations = Donation.objects.find_donations_by_contact_amount_currency_and_dates(
                    contact=sub.contact,
                    amount=sub.amount,
                    currency=sub.currency,
                    dates=[last_expected_date],
                )

                if not donations:
                    overdue_subs_data.append({'pk': sub.pk, 'overdue': days_since_last_expected})

        if not overdue_subs_data:
            return queryset.none()

        overdue_subs_data.sort(key=lambda x: x['overdue'], reverse=True)
        pks = [item['pk'] for item in overdue_subs_data]

        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pks)])
        return queryset.filter(pk__in=pks).order_by(preserved_order)