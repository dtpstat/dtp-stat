from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..factories import (
    GoalFactory, DonationFactory, SubscriptionFactory, CurrencyFactory, CurrencyPriceHistoryFactory
)


class GoalModelTest(TestCase):

    def setUp(self):
        self.today = date(2025,8,11)

    def test_clean_validation_end_date_before_start_date(self):
        """TC-GOL-1: Test that validation fails if end_date is earlier than start_date."""
        goal = GoalFactory.build(
            start_date=self.today,
            end_date=self.today - timedelta(days=1)
        )
        with self.assertRaises(ValidationError):
            goal.full_clean()

    def test_days_until_end_property(self):
        """TC-GOL-2: Verify the calculation for future and past goals."""
        future_goal = GoalFactory(end_date=self.today + timedelta(days=10))
        self.assertEqual(future_goal.days_until_end, 10)

        past_goal = GoalFactory(end_date=self.today - timedelta(days=10))
        self.assertEqual(past_goal.days_until_end, 0)

    def test_current_amount_raised_property(self):
        """TC-GOL-3: Verify it correctly sums confirmed donations within the goal's date range."""
        goal = GoalFactory(start_date=self.today, end_date=self.today + timedelta(days=30))
        
        # Donations that should be counted
        DonationFactory(
            confirmed=True, amount_in_base_currency=Decimal('100.00'),
            donation_datetime=timezone.make_aware(
                timezone.datetime.combine(goal.start_date, timezone.datetime.min.time())
            )
        )
        DonationFactory(
            confirmed=True, amount_in_base_currency=Decimal('50.00'),
            donation_datetime=timezone.make_aware(
                timezone.datetime.combine(goal.end_date, timezone.datetime.min.time())
            )
        )

        # Donation that should be ignored (not confirmed)
        DonationFactory(
            confirmed=False, amount_in_base_currency=Decimal('1000.00'),
            donation_datetime=timezone.make_aware(
                timezone.datetime.combine(goal.start_date, timezone.datetime.min.time())
            )
        )
        
        # Donation that should be ignored (outside date range)
        DonationFactory(
            confirmed=True, amount_in_base_currency=Decimal('2000.00'),
            donation_datetime=timezone.make_aware(
                timezone.datetime.combine(goal.start_date - timedelta(days=1), timezone.datetime.min.time())
            )
        )

        self.assertEqual(goal.current_amount_raised, Decimal('150.00'))

    def test_proposal_contribution_property(self):
        """TC-GOL-4: Verify it calculates projected income from active subscriptions."""
        goal = GoalFactory(
            start_date=self.today - timedelta(days=30),
            end_date=self.today + timedelta(days=50) # Approx 1.6 months left
        )
        currency = CurrencyFactory(code="USD")
        CurrencyPriceHistoryFactory(currency=currency, price=Decimal('1.50'))

        # This subscription should have 1 payment date within the goal's remaining timeframe
        SubscriptionFactory(
            active=True, currency=currency, amount=Decimal('10.00'),
            frequency='monthly', start_date=self.today - timedelta(days=45)
        )

        # This subscription should have 2 payment dates
        SubscriptionFactory(
            active=True, currency=currency, amount=Decimal('20.00'),
            frequency='monthly', start_date=self.today - timedelta(days=15)
        )

        # Expected: (2 * 10 * 1.5) + (2 * 20 * 1.5) = 30 + 60 = 90
        self.assertEqual(goal.proposal_contribution, Decimal('90.00'))

    def test_proposal_contribution_for_expired_goal(self):
        """TC-GOL-5: Ensure the contribution is zero for goals that have already ended."""
        goal = GoalFactory(end_date=self.today - timedelta(days=1))
        self.assertEqual(goal.proposal_contribution, 0)
