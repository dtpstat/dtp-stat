from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..factories import SubscriptionFactory, DonationFactory
from ..models import Subscription


class SubscriptionModelTest(TestCase):

    def setUp(self):
        self.today = date(2025,8,11)

    def test_clean_validation_end_date_before_start_date(self):
        """TC-SUB-1: Test that validation fails if end_date is earlier than start_date."""
        sub = SubscriptionFactory.build(
            start_date=self.today,
            end_date=self.today - timedelta(days=1)
        )
        with self.assertRaises(ValidationError):
            sub.full_clean()

    def test_is_active_property(self):
        """TC-SUB-2: Verify the logic for active, future, and past subscriptions."""
        self.assertTrue(SubscriptionFactory(active=True).is_active)
        self.assertFalse(SubscriptionFactory(inactive=True).is_active)
        self.assertFalse(SubscriptionFactory(future=True).is_active)

    def test_get_payment_dates_method(self):
        """TC-SUB-3: Test the generation of payment dates."""
        # Weekly subscription for 2 weeks
        sub_weekly = SubscriptionFactory(
            frequency='weekly',
            start_date=self.today,
            end_date=self.today + timedelta(days=13) # Should generate 2 dates
        )
        self.assertEqual(len(sub_weekly.get_payment_dates()), 2)

        # Monthly subscription for 3 months
        sub_monthly = SubscriptionFactory(
            frequency='monthly',
            start_date=self.today,
            end_date=self.today + timedelta(days=85) # Should generate 3 dates
        )
        self.assertEqual(len(sub_monthly.get_payment_dates()), 3)

    def test_last_expected_and_days_since_properties(self):
        """TC-SUB-4: Verify properties for new and ongoing subscriptions."""
        sub_future = SubscriptionFactory(future=True)
        self.assertIsNone(sub_future.last_expected_date)

        start = self.today - timedelta(days=40)
        sub_active = SubscriptionFactory(start_date=start, frequency='monthly')
        
        # Last expected date should be ~10 days ago (40 days ago - 30 days for first payment)
        expected_date = start + timedelta(days=31)
        self.assertEqual(sub_active.last_expected_date, expected_date)
        self.assertEqual(sub_active.days_since_last_expected, (self.today - expected_date).days)

    def test_disable_method(self):
        """TC-SUB-5: Test that calling disable() correctly sets the end_date."""
        sub = SubscriptionFactory(active=True)
        disable_date = self.today + timedelta(days=10)
        sub.disable(on_date=disable_date)
        self.assertEqual(sub.end_date, disable_date)

    def test_check_donation_success(self):
        """TC-SUB-6: Verify it returns True when a matching donation exists."""
        sub: Subscription = SubscriptionFactory(active=True, start_date=self.today - timedelta(days=32))
        
        # Create a donation that matches the last expected payment
        DonationFactory(
            contact=sub.contact,
            amount=sub.amount,
            currency=sub.currency,
            donation_datetime=timezone.make_aware(
                timezone.datetime.combine(sub.last_expected_date, timezone.datetime.min.time())
            )
        )
        
        self.assertTrue(sub.check_donation())
        sub.refresh_from_db()
        self.assertIsNone(sub.end_date) # Subscription should not be disabled

    def test_check_donation_failure_and_disable(self):
        """TC-SUB-7: Verify it returns False and disables the subscription if no donation is found."""
        sub = SubscriptionFactory(active=True, start_date=self.today - timedelta(days=35))
        last_date = sub.last_expected_date
        
        self.assertFalse(sub.check_donation(disable=True))
        
        sub.refresh_from_db()
        self.assertEqual(sub.end_date, last_date)

    def test_active_subscriptions_manager_method(self):
        """TC-SUB-8: Ensure the manager method returns only currently active subscriptions."""
        SubscriptionFactory(active=True)
        SubscriptionFactory(inactive=True)
        SubscriptionFactory(future=True)
        
        self.assertEqual(Subscription.objects.active_subscriptions().count(), 1)
