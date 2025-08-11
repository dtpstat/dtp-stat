from decimal import Decimal
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from ..models import Level, Contact, Goal, Subscription, Donation

class LevelModelTests(TestCase):
    """Tests for the Level model."""

    def test_level_creation(self):
        """Test that a Level can be created successfully."""
        level = Level.objects.create(name="Gold", description="Top tier")
        self.assertEqual(level.name, "Gold")
        self.assertEqual(level.description, "Top tier")
        self.assertIsNotNone(level.created_at)
        self.assertIsNotNone(level.updated_at)

    def test_level_str_representation(self):
        """Test the __str__ method of the Level model."""
        level = Level.objects.create(name="Silver")
        self.assertEqual(str(level), "Silver")

    def test_level_name_is_unique(self):
        """Test that the Level 'name' field enforces uniqueness."""
        Level.objects.create(name="Bronze")
        with self.assertRaises(IntegrityError):
            Level.objects.create(name="Bronze")


class ContactModelTests(TestCase):
    """Tests for the Contact model."""

    def test_contact_creation_with_email(self):
        """Test that a Contact can be created with an email."""
        contact = Contact.objects.create(email="test@example.com")
        self.assertEqual(contact.email, "test@example.com")
        self.assertEqual(contact.status, "Active") # Test default status

    def test_contact_str_representation(self):
        """Test the __str__ method shows the email or a fallback."""
        contact1 = Contact.objects.create(email="donor1@example.com")
        contact2 = Contact.objects.create(phone="+1234567890")
        self.assertEqual(str(contact1), f"Contact {contact1.id}")
        self.assertEqual(str(contact2), f"Contact {contact2.id}")

    def test_contact_email_is_unique(self):
        """Test that the Contact 'email' field enforces uniqueness."""
        Contact.objects.create(email="unique@example.com")
        with self.assertRaises(IntegrityError):
            Contact.objects.create(email="unique@example.com")

    def test_contact_clean_method_fails_if_no_contact_info(self):
        """Test validation fails if no email, telegram, or phone is provided."""
        contact = Contact()
        with self.assertRaises(ValidationError) as cm:
            contact.full_clean()
        self.assertIn("A contact must have at least an email", str(cm.exception))


class GoalModelTests(TestCase):
    """Tests for the Goal model."""

    def test_goal_creation(self):
        """Test that a Goal can be created successfully."""
        start = date.today()
        end = start + timedelta(days=30)
        goal = Goal.objects.create(
            target_amount=Decimal("5000.00"),
            start_date=start,
            end_date=end
        )
        self.assertEqual(goal.target_amount, Decimal("5000.00"))
        self.assertEqual(goal.start_date, start)

    def test_goal_str_representation(self):
        """Test the __str__ method of the Goal model."""
        goal = Goal.objects.create(
            target_amount="1000",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31)
        )
        expected_str = "Goal: 2025-01-01 to 2025-12-31"
        self.assertEqual(str(goal), expected_str)

    def test_goal_clean_method_fails_with_invalid_dates(self):
        """Test validation fails if end_date is before start_date."""
        start = date.today()
        end = start - timedelta(days=1)
        goal = Goal(target_amount="100", start_date=start, end_date=end)
        with self.assertRaisesRegex(ValidationError, "The end date cannot be before the start date."):
            goal.full_clean()

    def test_goal_target_amount_must_be_positive(self):
        """Test that target_amount cannot be zero or negative."""
        goal = Goal(target_amount="-100", start_date=date.today(), end_date=date.today())
        with self.assertRaises(ValidationError):
            goal.full_clean() # MinValueValidator is checked during full_clean


class SubscriptionModelTests(TestCase):
    """Tests for the Subscription model."""

    def setUp(self):
        self.contact = Contact.objects.create(email="subscriber@example.com")
        self.level = Level.objects.create(name="Patron")

    def test_subscription_creation(self):
        """Test successful creation of a Subscription."""
        sub = Subscription.objects.create(
            contact=self.contact,
            level=self.level,
            amount="25.00",
            currency="USD",
            start_date=timezone.now(),
            frequency=Subscription.Frequency.MONTHLY
        )
        self.assertTrue(sub.is_active) # Test default value
        self.assertEqual(sub.contact, self.contact)
        self.assertEqual(sub.level, self.level)

    def test_deleting_contact_is_protected(self):
        """Test that deleting a Contact with a Subscription is protected."""
        Subscription.objects.create(
            contact=self.contact,
            amount="10.00",
            currency="EUR",
            start_date=timezone.now(),
            frequency='weekly'
        )
        with self.assertRaises(ProtectedError):
            self.contact.delete()

    def test_deleting_level_sets_subscription_level_to_null(self):
        """Test that deleting a Level sets the corresponding field on Subscription to NULL."""
        sub = Subscription.objects.create(
            contact=self.contact,
            level=self.level,
            amount="50.00",
            currency="GBP",
            start_date=timezone.now(),
            frequency='monthly'
        )
        self.level.delete()
        sub.refresh_from_db()
        self.assertIsNone(sub.level)


class DonationModelTests(TestCase):
    """Tests for the Donation model."""

    @classmethod
    def setUp(self):
        self.contact1 = Contact.objects.create(email="donor@example.com")
        self.contact2 = Contact.objects.create(email="anotherdonor@example.com")
        self.subscription = Subscription.objects.create(
            contact=self.contact1,
            amount="15.00",
            currency="USD",
            start_date=timezone.now(),
            frequency='monthly'
        )

    def test_one_off_donation_creation(self):
        """Test creating a standard, one-off donation."""
        donation = Donation.objects.create(
            contact=self.contact1,
            amount="100.00",
            currency="USD",
            amount_in_base_currency="100.00"
        )
        self.assertFalse(donation.is_confirmed) # Test default
        self.assertEqual(donation.contact, self.contact1)

    def test_anonymous_donation_creation(self):
        """Test creating a donation with no contact."""
        donation = Donation.objects.create(
            amount="50.00",
            currency="EUR",
            amount_in_base_currency="55.00"
        )
        self.assertIsNone(donation.contact)

    def test_donation_linked_to_subscription(self):
        """Test creating a donation that is part of a subscription."""
        donation = Donation.objects.create(
            contact=self.subscription.contact,
            subscription=self.subscription,
            amount=self.subscription.amount,
            currency=self.subscription.currency,
            amount_in_base_currency=self.subscription.amount
        )
        self.assertEqual(donation.subscription, self.subscription)
        self.assertEqual(donation.contact, self.subscription.contact)

    def test_validation_fails_if_subscription_contact_mismatches(self):
        """Test that clean() fails if donation.contact != subscription.contact."""
        donation = Donation(
            contact=self.contact2, # Mismatched contact
            subscription=self.subscription,
            amount="15.00",
            currency="USD",
            amount_in_base_currency="15.00"
        )
        with self.assertRaisesRegex(ValidationError, "does not match the contact on the subscription"):
            donation.full_clean()

    def test_validation_fails_for_confirmed_donation_without_base_currency(self):
        """Test clean() fails if is_confirmed=True and amount_in_base_currency is None."""
        donation = Donation(
            contact=self.contact1,
            amount="200.00",
            currency="JPY",
            is_confirmed=True,
            amount_in_base_currency=None # Missing required field
        )
        with self.assertRaises(ValidationError) as cm:
            donation.full_clean()
        self.assertIn('amount_in_base_currency', cm.exception.error_dict)
    
    def test_validation_passes_for_confirmed_donation_with_base_currency(self):
        """Test clean() passes if is_confirmed=True and amount_in_base_currency is set."""
        donation = Donation(
            contact=self.contact1,
            amount="200.00",
            currency="JPY",
            is_confirmed=True,
            amount_in_base_currency="1.50"
        )
        try:
            donation.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")

    def test_deleting_subscription_sets_donation_subscription_to_null(self):
        """Test on_delete=SET_NULL for the subscription field."""
        donation = Donation.objects.create(
            contact=self.contact1,
            subscription=self.subscription,
            amount="15.00",
            currency="USD",
            amount_in_base_currency="15.00"
        )
        self.subscription.delete()
        donation.refresh_from_db()
        self.assertIsNone(donation.subscription)