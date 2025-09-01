from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from ..factories import ContactFactory
from ..models import Contact


class ContactModelTest(TestCase):

    def test_successful_creation(self):
        """TC-CON-1: Create a Contact with valid and sufficient data (e.g., just an email)."""
        contact = ContactFactory()
        self.assertIsNotNone(contact.pk)
        self.assertIn('@', contact.email)

    def test_str_method(self):
        """TC-CON-2: Verify the string representation of a Contact object."""
        contact = ContactFactory()
        self.assertEqual(str(contact), f"Contact {contact.pk}")

    def test_validation_failure_no_contact_info(self):
        """TC-CON-3: Ensure that creating a Contact with no email, telegram, or phone fails validation."""
        # Use .build() to create an in-memory instance without hitting the DB
        contact = ContactFactory.build(email=None, telegram="", phone="")
        with self.assertRaises(ValidationError):
            contact.full_clean()

    def test_unique_email_constraint(self):
        """TC-CON-4: Test that creating two contacts with the same email raises an error."""
        ContactFactory(email="test@example.com")
        with self.assertRaises(IntegrityError):
            ContactFactory(email="test@example.com")

    def test_default_status(self):
        """TC-CON-5: Verify that a new contact defaults to the 'Active' status."""
        contact = ContactFactory()
        self.assertEqual(contact.status, Contact.Status.ACTIVE)
