from datetime import datetime

from django.test import TestCase

from killstats.templatetags.killstats import current_month


class CurrentMonthFilterTest(TestCase):
    def test_current_month_with_valid_month(self):
        """Test whether a valid month value is handled correctly."""
        month = current_month(3)
        self.assertEqual(month, "March")

    def test_current_month_with_invalid_month(self):
        """Test whether an invalid month value is handled correctly."""
        month = current_month(14)
        self.assertEqual(month, datetime.now().strftime("%B"))
