from decimal import Decimal
from django.test import TestCase
from django.utils import timezone

from ..factories import CurrencyFactory, CurrencyPriceHistoryFactory
from ..models import CurrencyPriceHistory


class CurrencyAndPriceHistoryModelTest(TestCase):

    def test_currency_str_method(self):
        """TC-CUR-1: Verify the string representation of a Currency object."""
        currency = CurrencyFactory(code="USD", name="US Dollar")
        self.assertEqual(str(currency), "(USD) US Dollar")

    def test_latest_price_property_with_history(self):
        """TC-CUR-2: Test that the property returns the price from the most recent record."""
        currency = CurrencyFactory()
        now = timezone.now()
        
        CurrencyPriceHistoryFactory(
            currency=currency, 
            datetime=now - timezone.timedelta(days=2), 
            price=Decimal('1.0')
        )
        latest_price_history = CurrencyPriceHistoryFactory(
            currency=currency, 
            datetime=now - timezone.timedelta(days=1), 
            price=Decimal('1.5')
        )

        self.assertEqual(currency.latest_price, latest_price_history.price)
        self.assertEqual(currency.latest_price, Decimal('1.5'))

    def test_latest_price_property_no_history(self):
        """TC-CUR-3: Test that the property returns None if no price history exists."""
        currency = CurrencyFactory()
        self.assertIsNone(currency.latest_price)

    def test_on_delete_cascade_behavior(self):
        """TC-CPH-1: Verify that deleting a Currency also deletes its CurrencyPriceHistory records."""
        currency = CurrencyFactory()
        CurrencyPriceHistoryFactory(currency=currency)
        
        self.assertEqual(CurrencyPriceHistory.objects.count(), 1)
        currency.delete()
        self.assertEqual(CurrencyPriceHistory.objects.count(), 0)
