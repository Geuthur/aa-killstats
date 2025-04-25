from django.test import TestCase
from django.utils import timezone
from eveuniverse.models import EveEntity, EveGroup, EveType

from allianceauth.eveonline.evelinks import eveimageserver
from allianceauth.eveonline.models import EveCharacter

from killstats.models.killboard import Killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.models.killstatsaudit"


class TestKillboardtModel(TestCase):
    @classmethod
    def setUp(self):
        load_allianceauth()
        load_killstats_all()
        self.killmail = Killmail.objects.get(killmail_id=119303113)
        self.killmail2 = Killmail.objects.create(
            killmail_id=119303114,
            killmail_date=timezone.now(),
            victim=EveEntity.objects.get(id=1001),
            victim_ship=EveType.objects.get(id=670),
            victim_corporation_id=20000001,
            victim_alliance_id=30000001,
            hash="hash",
            victim_total_value=1000,
            victim_fitted_value=500,
            victim_destroyed_value=500,
            victim_dropped_value=500,
            victim_region_id=1001,
            victim_solar_system_id=20000001,
            victim_position_x=1.0,
            victim_position_y=1.0,
            victim_position_z=1.0,
        )

    def test_is_corp(self):
        self.assertTrue(self.killmail.is_corp([20000001]))
        self.assertFalse(self.killmail2.is_corp([30000001]))

    def test_is_ally(self):
        self.assertFalse(self.killmail.is_alliance([20000001]))
        self.assertTrue(self.killmail2.is_alliance([30000001]))

    def test_is_structure(self):
        self.killmail.victim_ship.eve_group.eve_category_id = 65
        self.assertTrue(self.killmail.is_structure())
        self.killmail.victim_ship.eve_group.eve_category_id = 0
        self.assertFalse(self.killmail.is_structure())

    def test_is_mobile(self):
        self.killmail.victim_ship.eve_group.eve_category_id = 22
        self.assertTrue(self.killmail.is_mobile())
        self.killmail.victim_ship.eve_group.eve_category_id = 0
        self.assertFalse(self.killmail.is_mobile())

    def test_is_capsule(self):
        self.assertFalse(self.killmail.is_capsule())
        self.killmail.victim_ship.eve_group = EveGroup.objects.get(id=29)
        self.assertTrue(self.killmail.is_capsule())

    def test_get_month(self):
        self.killmail.killmail_date = timezone.datetime(
            2023, 10, 1, tzinfo=timezone.utc
        )
        self.assertTrue(self.killmail.get_month(10))
        self.killmail.killmail_date = timezone.datetime(
            2023, 1, 30, tzinfo=timezone.utc
        )
        self.assertFalse(self.killmail.get_month(9))

    def test_threshold(self):
        self.assertTrue(self.killmail.threshold(500_000))
        self.assertFalse(self.killmail.threshold(150_000_000))

    def test_str(self):
        self.assertEqual(str(self.killmail), "Killmail 119303113")

    def test_get_victim_name(self):
        expected_url = "Gneuten"
        self.assertEqual(self.killmail.get_or_unknown_victim_name(), expected_url)

        self.killmail.victim = None
        expected_url = "Unknown"
        self.assertEqual(self.killmail.get_or_unknown_victim_name(), expected_url)

    def test_get_victim_ship_name(self):
        expected_url = "Victim Ship I"
        self.assertEqual(self.killmail.get_or_unknown_victim_ship_name(), expected_url)

        self.killmail.victim_ship = None
        expected_url = "Unknown"

    def test_evaluate_zkb_link(self):
        expected_url = "https://zkillboard.com/character/1001/"
        self.assertEqual(self.killmail.evaluate_zkb_link(), expected_url)

        self.killmail.victim.category = "corporation"
        expected_url = "https://zkillboard.com/corporation/20000001/"
        self.assertEqual(self.killmail.evaluate_zkb_link(), expected_url)

        self.killmail.victim.category = "alliance"
        expected_url = "https://zkillboard.com/alliance/30000001/"
        self.assertEqual(self.killmail.evaluate_zkb_link(), expected_url)
