from django.test import TestCase
from django.db.utils import IntegrityError

from ..factories import LevelFactory


class LevelModelTest(TestCase):

    def test_successful_creation(self):
        """TC-LVL-1: Ensure a Level can be created with a name and description."""
        level = LevelFactory()
        self.assertIsNotNone(level.pk)
        self.assertIn('Level', level.name)

    def test_str_method(self):
        """TC-LVL-2: Verify the string representation of a Level object."""
        level = LevelFactory(name="Gold Tier")
        self.assertEqual(str(level), "Gold Tier")

    def test_unique_name_constraint(self):
        """TC-LVL-3: Test that creating two levels with the same name raises an error."""
        LevelFactory(name="Unique Name")
        with self.assertRaises(IntegrityError):
            LevelFactory(name="Unique Name")
