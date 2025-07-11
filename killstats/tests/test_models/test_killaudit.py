# Django
from django.test import TestCase

# AA Killstats
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tests.testdata.generate_killstats import (
    create_allianceaudit_from_character_id,
    create_corporationaudit_from_character_id,
)
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_eveuniverse import load_eveuniverse

MODULE_PATH = "killstats.models.killstatsaudit"


class TestKillstatsAuditModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()

        cls.audit1 = create_corporationaudit_from_character_id(
            1001,
        )
        cls.audit2 = create_allianceaudit_from_character_id(
            1007,
        )

    def test_str(self):
        self.audit = CorporationsAudit.objects.get(corporation__corporation_id=2001)
        self.assertEqual(str(self.audit), "Hell RiderZ's Killstats Data")

    def test_alliance_str(self):
        self.audit = AlliancesAudit.objects.get(alliance__alliance_id=3002)
        self.assertEqual(str(self.audit), "Eulen Sigma's Killstats Data")
