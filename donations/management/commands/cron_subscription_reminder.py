import logging
from urllib.parse import urlencode

from constance import config
from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from donations.infrastructure import send_telegram_message
from donations.models import Subscription

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cron job to send subscription reminder emails'

    def handle(self, *args, **kwargs):
        logger.info("Starting cron_subscription_reminder job")
        if not config.DONATES_SUBSCRIPTION_ALERT_CHAT_ID:
            logger.info("No chat id found. Cron_subscription_reminder job skipped.")
            return
        overdue_subscription_count = Subscription.objects.with_overdue_donations().count()
        url = reverse(f'admin:donations_subscription_changelist')
        filter_str = urlencode({'without_expected_donation': 'true'})
        url = f'{settings.PRODUCTION_HOST}{url}?{filter_str}'
        message = f'There are {overdue_subscription_count} overdue subscriptions. Please check {url} for more details.'
        send_telegram_message(config.DONATES_SUBSCRIPTION_ALERT_CHAT_ID, message)
