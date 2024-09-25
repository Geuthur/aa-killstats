from datetime import datetime

from django.test import TestCase

from allianceauth.eveonline.evelinks import eveimageserver
from allianceauth.eveonline.models import EveCharacter

from killstats.models.killboard import EveEntity, EveType, Killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.models.killstatsaudit"


class TestKillboardtModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cls.victim = EveEntity.objects.get(id=1005)
        cls.victim_ship = EveType.objects.get(id=670)
        cls.victim_ship2 = EveType.objects.get(id=17634)
        cls.killmail = Killmail.objects.create(
            killmail_id=1,
            killmail_date=datetime.now(),
            victim=cls.victim,
            victim_ship=cls.victim_ship,
            victim_corporation_id=2001,
            hash="hash1",
            attackers=[
                {"character_id": 1001, "corporation_id": 2001, "alliance_id": 3001},
                {"character_id": 1002, "corporation_id": 2002, "alliance_id": 3002},
            ],
            victim_total_value=1_000_000,
        )

        cls.killmail2 = Killmail.objects.create(
            killmail_id=2,
            killmail_date=datetime.now(),
            victim=cls.victim,
            victim_ship=cls.victim_ship2,
            victim_corporation_id=2001,
            hash="hash2",
            attackers=[
                {"character_id": 1004, "corporation_id": 2001, "alliance_id": 3001},
                {"character_id": 1005, "corporation_id": 2002, "alliance_id": 3002},
            ],
            victim_total_value=100_000_000,
        )

    def test_is_corp(self):
        self.assertTrue(self.killmail.is_corp([2001]))
        self.assertTrue(self.killmail.is_corp([2001]))
        self.assertFalse(self.killmail.is_corp([3001]))

    def test_is_ally(self):
        self.assertFalse(self.killmail.is_alliance([2001]))
        self.assertFalse(self.killmail.is_alliance([2001]))
        self.assertTrue(self.killmail.is_alliance([3001]))

    def test_is_structure(self):
        self.killmail.victim_ship.eve_group.eve_category_id = 65
        self.assertTrue(self.killmail.is_structure())
        self.killmail.victim_ship.eve_group.eve_category_id = 1
        self.assertFalse(self.killmail.is_structure())

    def test_is_mobile(self):
        self.killmail.victim_ship.eve_group.eve_category_id = 22
        self.assertTrue(self.killmail.is_mobile())
        self.killmail.victim_ship.eve_group.eve_category_id = 1
        self.assertFalse(self.killmail.is_mobile())

    def test_is_capsule(self):
        self.assertTrue(self.killmail.is_capsule())
        self.assertFalse(self.killmail2.is_capsule())

    def test_get_month(self):
        self.killmail.killmail_date = datetime(2023, 10, 1)
        self.assertTrue(self.killmail.get_month(10))
        self.assertFalse(self.killmail.get_month(9))

    def test_threshold(self):
        killmail = Killmail.objects.get(killmail_id=1)
        self.assertTrue(killmail.threshold(500_000))
        self.assertFalse(killmail.threshold(1_500_000))

    def test_str(self):
        self.assertEqual(str(self.killmail), "Killmail 1")

    def test_get_image_url(self):
        expected_url = eveimageserver._eve_entity_image_url(
            self.victim.category, self.victim.id, 32
        )
        self.assertEqual(self.killmail.get_image_url(), expected_url)
