# AA Killstats
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tests import AuthTestCase
from killstats.tests.testdata.killstats import (
    AlliancesAuditFactory,
    CorporationsAuditFactory,
)

MODULE_PATH = "killstats.models.killstatsaudit"


class TestKillstatsAuditModel(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.audit1 = CorporationsAuditFactory(
            corporation__corporation_id=2001,
            corporation__corporation_name="Hell RiderZ",
        )
        cls.audit2 = AlliancesAuditFactory(
            alliance__alliance_id=3002, alliance__alliance_name="Eulen Sigma"
        )

    def test_str(self):
        self.audit = CorporationsAudit.objects.get(corporation__corporation_id=2001)
        self.assertEqual(str(self.audit), "Hell RiderZ's Killstats Data")

    def test_alliance_str(self):
        self.audit = AlliancesAudit.objects.get(alliance__alliance_id=3002)
        self.assertEqual(str(self.audit), "Eulen Sigma's Killstats Data")
