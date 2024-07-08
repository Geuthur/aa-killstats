import calendar
from datetime import datetime

from django.test import TestCase

from killstats.templatetags.killstats import current_month


class CurrentMonthFilterTest(TestCase):
    def test_current_month_with_valid_month(self):
        """Testet, ob ein gültiger Monatswert korrekt gehandhabt wird."""
        month = current_month(3)
        self.assertEqual(month, "March")

    def test_current_month_with_invalid_month(self):
        """Testet, ob ein ungültiger Monatswert den aktuellen Monat zurückgibt."""
        month = current_month(14)
        self.assertEqual(month, "July")
