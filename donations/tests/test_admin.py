from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ..models import Level, Contact, Goal, Subscription, Donation
from ..admin import LevelAdmin, ContactAdmin, GoalAdmin, SubscriptionAdmin, DonationAdmin

# Get the User model, whether it's the default or a custom one
User = get_user_model()

# Replace 'your_app_name' with the actual name of your Django app
APP_NAME = 'donations' 

class AdminTestCase(TestCase):
    """
    A base TestCase for admin tests that handles user creation,
    login, and basic data setup.
    """
    def setUp(self):
        # Create a superuser for admin access
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client = Client()
        self.client.login(username='admin', password='password123')

        # Mock AdminSite instance
        self.site = AdminSite()

        # Create sample data for testing
        self.level = Level.objects.create(name="Gold", description="Top tier")
        self.contact = Contact.objects.create(
            email="test@example.com",
            telegram="testuser",
            status=Contact.Status.ACTIVE
        )
        self.goal = Goal.objects.create(
            target_amount=Decimal('5000.00'),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        self.subscription = Subscription.objects.create(
            contact=self.contact,
            level=self.level,
            amount=Decimal('50.00'),
            currency='USD',
            frequency=Subscription.Frequency.MONTHLY,
            start_date=timezone.now()
        )
        self.donation = Donation.objects.create(
            contact=self.contact,
            subscription=self.subscription,
            amount=Decimal('50.00'),
            currency='USD',
            amount_in_base_currency=Decimal('50.00'),
            is_confirmed=True
        )

    def _get_admin_url(self, model, view_name, args=None):
        """Helper to generate admin URLs."""
        return reverse(f'admin:{APP_NAME}_{model._meta.model_name}_{view_name}', args=args)


class TestLevelAdmin(AdminTestCase):
    def test_changelist_view(self):
        """Test that the Level changelist page loads and displays correct fields."""
        url = self._get_admin_url(Level, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.level.name)
        # Check for list_display fields
        self.assertContains(response, 'Name')
        self.assertContains(response, 'Created at')

    def test_change_view(self):
        """Test that the Level change page loads."""
        url = self._get_admin_url(Level, 'change', args=[self.level.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.level.name)

    def test_search(self):
        """Test search functionality for LevelAdmin."""
        url = self._get_admin_url(Level, 'changelist')
        response = self.client.get(url, {'q': 'Gold'})
        self.assertContains(response, self.level.name)
        response = self.client.get(url, {'q': 'NonExistent'})
        self.assertNotContains(response, self.level.name)


class TestContactAdmin(AdminTestCase):
    def test_changelist_view(self):
        """Test that the Contact changelist page loads and displays correct fields."""
        url = self._get_admin_url(Contact, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.contact.email)
        # Check for list_display fields
        self.assertContains(response, 'Email address')
        self.assertContains(response, 'Status')

    def test_change_view_and_inlines(self):
        """Test that the Contact change page loads and contains inlines."""
        url = self._get_admin_url(Contact, 'change', args=[self.contact.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check for Subscription inline
        self.assertContains(response, 'id_subscriptions-TOTAL_FORMS')
        self.assertContains(response, self.subscription.get_frequency_display())
        # Check for Donation inline
        self.assertContains(response, 'id_donations-TOTAL_FORMS')
        self.assertContains(response, self.donation.amount)

    def test_search(self):
        """Test search functionality for ContactAdmin."""
        url = self._get_admin_url(Contact, 'changelist')
        response = self.client.get(url, {'q': 'test@example.com'})
        self.assertContains(response, self.contact.email)
        response = self.client.get(url, {'q': 'testuser'})
        self.assertContains(response, self.contact.telegram)


class TestGoalAdmin(AdminTestCase):
    def test_changelist_view(self):
        """Test that the Goal changelist page loads."""
        url = self._get_admin_url(Goal, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.goal))
        self.assertContains(response, 'Target amount')


class TestSubscriptionAdmin(AdminTestCase):
    def test_changelist_view(self):
        """Test that the Subscription changelist page loads."""
        url = self._get_admin_url(Subscription, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.subscription))
        self.assertContains(response, 'Contact')
        self.assertContains(response, 'Level')
        self.assertContains(response, 'Frequency')
        self.assertContains(response, 'Is active')

    def test_change_view_and_inlines(self):
        """Test that the Subscription change page loads and contains Donation inline."""
        url = self._get_admin_url(Subscription, 'change', args=[self.subscription.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check for Donation inline
        self.assertContains(response, 'id_donations-TOTAL_FORMS')
        self.assertContains(response, self.donation.amount)

    def test_search(self):
        """Test search functionality for SubscriptionAdmin."""
        url = self._get_admin_url(Subscription, 'changelist')
        response = self.client.get(url, {'q': 'test@example.com'})
        self.assertContains(response, str(self.subscription))


class TestDonationAdmin(AdminTestCase):
    def test_changelist_view(self):
        """Test that the Donation changelist page loads and custom method works."""
        url = self._get_admin_url(Donation, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Test the custom display method 'amount_with_currency'
        expected_amount_str = f"{self.donation.amount} {self.donation.currency}"
        self.assertContains(response, expected_amount_str)
        self.assertContains(response, 'Is confirmed')

    def test_change_view(self):
        """Test that the Donation change page loads."""
        url = self._get_admin_url(Donation, 'change', args=[self.donation.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Information')
        self.assertContains(response, self.donation.amount)

    def test_amount_with_currency_method(self):
        """Directly test the custom admin method."""
        donation_admin = DonationAdmin(Donation, self.site)
        result = donation_admin.amount_with_currency(self.donation)
        self.assertEqual(result, "50.00 USD")