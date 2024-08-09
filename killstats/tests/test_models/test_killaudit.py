from django.test import TestCase

from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.models.killstatsaudit"


class TestKillstatsAuditModel(TestCase):
    @classmethod
    def setUp(self):
        load_allianceauth()
        load_killstats_all()

    def test_str(self):
        self.audit = CorporationsAudit.objects.get(corporation__corporation_id=2001)
        self.assertEqual(str(self.audit), "Hell RiderZ's Killstats Data")

    def test_alliance_str(self):
        self.audit = AlliancesAudit.objects.get(alliance__alliance_id=3002)
        self.assertEqual(str(self.audit), "Eulen Sigma's Killstats Data")
