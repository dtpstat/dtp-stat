from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from donations.models import Subscription


class Command(BaseCommand):
    help = 'Cron job to deactivate subscriptions'

    def handle(self, *args, **kwargs):
        subscriptions = Subscription.objects.active_subscriptions()
        for subscription in subscriptions:
            with transaction.atomic():
                subscription.check_donation(disable=True)
