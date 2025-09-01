import logging
from datetime import timedelta

from constance import config
from django.core.management.base import BaseCommand
from django.utils import timezone

from donations.infrastructure import send_telegram_message
from donations.models import Donation, Goal, Subscription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cron job to send daily report to telegram'

    def handle(self, *args, **kwargs):
        logger.info("Starting cron_telegram_daily_report job")
        if not config.DONATES_REPORT_CHAT_ID:
            logger.info("No chat id found. Cron_telegram_daily_report job skipped.")
            return
        active_goal = Goal.objects.active_goal()
        if active_goal:
            today = timezone.now().date()
            tomorrow = today + timedelta(days=1)
            days_in_goal = (active_goal.end_date - active_goal.start_date).days

            total_donated = active_goal.current_amount_raised
            donated_today = Donation.objects.total_donated_in_range(today, today)
            passed_days = (today - active_goal.start_date).days
            norm_by_yesterday = (active_goal.target_amount / days_in_goal) * passed_days
            days_left = (active_goal.end_date - today).days
            needed_tomorrow = (active_goal.target_amount - total_donated) / days_left if days_left > 0 else 0

            expected_tomorrow = 0
            for subscription in Subscription.objects.active_subscriptions():
                expected_tomorrow += subscription.calculate_proposal_contribution_in_range(
                    start_date=tomorrow,
                    end_date=tomorrow,
                )

            message = f"""
🎯 Цель месяца: {active_goal.target_amount:,.0f} ₽
📊 Собрано всего: {total_donated:,.0f} ₽
📅 Сегодня собрано: {donated_today:,.0f} ₽
🧮 Норма к вчерашнему дню: {norm_by_yesterday:,.0f} ₽
🕓 Осталось дней: {days_left}
💸 Нужно собрать завтра: {needed_tomorrow:,.0f} ₽
🔔 Ожидается завтра по подпискам: {expected_tomorrow:,.0f} ₽
"""
            send_telegram_message(config.DONATES_REPORT_CHAT_ID, message)
            logger.info('Successfully sent daily report to telegram.')
        else:
            logger.info("No active goal found.")