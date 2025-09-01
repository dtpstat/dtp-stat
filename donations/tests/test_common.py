from datetime import timedelta

from django.test import TestCase
from time import sleep

from ..factories import ContactFactory


class TimeStampedModelTest(TestCase):
    """
    Tests for the TimeStampedModel abstract model.
    """

    def test_fields_auto_populated_on_creation(self):
        """
        TC-GEN-1: Verifies that created_at and updated_at are set automatically
        when a new object is created.
        """
        obj = ContactFactory()
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)
        self.assertAlmostEqual(obj.created_at, obj.updated_at, delta=timedelta(seconds=1))

    def test_updated_at_auto_updates_on_save(self):
        """
        TC-GEN-2: Verifies that updated_at is updated on save,
        while created_at remains unchanged.
        """
        contact = ContactFactory()
        original_created_at = contact.created_at
        original_updated_at = contact.updated_at

        # Sleep to ensure the updated_at timestamp will be different
        sleep(0.01)

        contact.email = "new.email@example.com"
        contact.save()
        contact.refresh_from_db()

        self.assertEqual(contact.created_at, original_created_at)
        self.assertGreater(contact.updated_at, original_updated_at)
