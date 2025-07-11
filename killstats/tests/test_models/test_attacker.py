# Django
from django.test import TestCase
from django.utils import timezone

# Alliance Auth (External Libs)
from eveuniverse.models import EveEntity, EveType

# AA Killstats
from killstats.tests.testdata.generate_killmail import create_attacker, create_killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_eveuniverse import load_eveuniverse

MODULE_PATH = "killstats.models.killstatsaudit"


class TestAttackertModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()
        cls.killmail = create_killmail(
            killmail_id=119303113,
            killmail_date=timezone.now(),
            victim=EveEntity.objects.get(id=1001),
            victim_ship=EveType.objects.get(id=670),
            victim_corporation_id=2001,
            victim_alliance_id=3001,
            hash="hash",
            victim_total_value=1000,
            victim_fitted_value=500,
            victim_destroyed_value=500,
            victim_dropped_value=500,
            victim_region_id=1001,
            victim_solar_system_id=2001,
            victim_position_x=1.0,
            victim_position_y=1.0,
            victim_position_z=1.0,
        )
        cls.attacker = create_attacker(
            killmail=cls.killmail,
            character=EveEntity.objects.get(id=1000),
            corporation=EveEntity.objects.get(id=1000125),
            alliance=EveEntity.objects.get(id=3001),
            ship=EveType.objects.get(id=670),
            damage_done=500,
            final_blow=True,
        )

    def test_evaluate_attacker_id(self):
        self.assertEqual(self.attacker.evaluate_attacker(), (1000, "CONCORD"))
        self.attacker.character = None
        self.assertEqual(self.attacker.evaluate_attacker(), (1000125, "CONCORD"))
        self.attacker.corporation = None
        self.assertEqual(self.attacker.evaluate_attacker(), (3001, "Voices of War"))
        self.attacker.alliance = None
        self.assertEqual(self.attacker.evaluate_attacker(), (0, "Unknown"))
