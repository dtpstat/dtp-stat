from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from ..factories import (
    DonationFactory, SubscriptionFactory, ContactFactory
)
from ..models import Donation


class DonationModelTest(TestCase):

    def test_creation_scenarios(self):
        """TC-DON-1: Test all valid creation scenarios."""
        # Anonymous
        anon_donation = DonationFactory()
        self.assertIsNotNone(anon_donation.pk)
        self.assertIsNone(anon_donation.contact)

        # From Contact
        contact_donation = DonationFactory(with_contact=True)
        self.assertIsNotNone(contact_donation.pk)
        self.assertIsNotNone(contact_donation.contact)

        # From Subscription
        sub_donation = DonationFactory(from_subscription=True)
        self.assertIsNotNone(sub_donation.pk)
        self.assertIsNotNone(sub_donation.subscription)
        self.assertEqual(sub_donation.contact, sub_donation.subscription.contact)

        # Confirmed
        confirmed_donation = DonationFactory(confirmed=True, with_contact=True)
        self.assertTrue(confirmed_donation.is_confirmed)
        self.assertIsNotNone(confirmed_donation.amount_in_base_currency)

    def test_clean_contact_mismatch(self):
        """TC-DON-2: Test validation failure when a donation's contact does not match its subscription's contact."""
        subscription = SubscriptionFactory()
        other_contact = ContactFactory()
        
        with self.assertRaises(ValidationError) as cm:
            DonationFactory.build(
                subscription=subscription,
                contact=other_contact
            ).full_clean()
        
        self.assertIn('contact', cm.exception.message_dict)
        self.assertIn('does not match the contact on the subscription.', cm.exception.message_dict['contact'][0])

    def test_clean_confirmed_without_base_amount(self):
        """TC-DON-3: Test validation failure when a donation is confirmed but amount_in_base_currency is None."""
        donation = DonationFactory.build(confirmed=True, amount_in_base_currency=None)
        with self.assertRaises(ValidationError) as cm:
            donation.full_clean()
        self.assertIn('amount_in_base_currency', cm.exception.message_dict)

    def test_on_delete_protect_for_contact(self):
        """TC-DON-4: Ensure a Contact with donations cannot be deleted."""
        contact = ContactFactory()
        DonationFactory(contact=contact)
        
        with self.assertRaises(ProtectedError):
            contact.delete()

    def test_on_delete_set_null_for_subscription(self):
        """TC-DON-5: Ensure deleting a Subscription sets the foreign key on Donation to NULL."""
        donation = DonationFactory(from_subscription=True)
        self.assertIsNotNone(donation.subscription)
        
        donation.subscription.delete()
        donation.refresh_from_db()
        
        self.assertIsNone(donation.subscription)
