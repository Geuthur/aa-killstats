from django.test import TestCase
from django.utils import timezone
from eveuniverse.models import EveEntity, EveGroup, EveType

from allianceauth.eveonline.evelinks import eveimageserver
from allianceauth.eveonline.models import EveCharacter

from killstats.models.killboard import Attacker, Killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.models.killstatsaudit"


class TestAttackertModel(TestCase):
    @classmethod
    def setUp(self):
        load_allianceauth()
        load_killstats_all()
        self.killmail = Killmail.objects.get(killmail_id=119303113)
        self.attacker = Attacker.objects.filter(killmail=self.killmail).first()

    def test_get_or_unknown_ship_name(self):
        self.assertEqual(self.attacker.get_or_unknown_ship_name(), "Attacker Ship I")
        self.attacker.ship = None
        self.assertEqual(self.attacker.get_or_unknown_ship_name(), "Unknown")

    def test_evaluate_attacker_id(self):
        self.assertEqual(self.attacker.evaluate_attacker(), (1000, "CONCORD"))
        self.attacker.character = None
        self.assertEqual(self.attacker.evaluate_attacker(), (1000125, "CONCORD"))
        self.attacker.corporation = None
        self.attacker.alliance = EveEntity.objects.get(id=30000001)
        self.assertEqual(self.attacker.evaluate_attacker(), (30000001, "Voices of War"))
        self.attacker.alliance = None
        self.assertEqual(self.attacker.evaluate_attacker(), (0, "Unknown"))
