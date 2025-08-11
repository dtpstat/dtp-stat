from django.db import models
from django.db.models import Q
from django.utils import timezone


class SubscriptionManager(models.Manager):
    def active_subscriptions(self):
        """Returns a queryset of all active subscriptions."""
        today = timezone.now().date()

        return self.get_queryset().filter(
            start_date__lte=today,
        ).filter(
            Q(subscription_end__gte=today) | Q(subscription_end__isnull=True),
        )