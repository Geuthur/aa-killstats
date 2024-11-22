from unittest.mock import MagicMock, patch

from django.test import TestCase

from app_utils.testing import create_user_from_evecharacter

from killstats.api.killboard_manager import _get_character_details_victim
from killstats.api.killstats.api_helper import get_killstats_halls
from killstats.models.killboard import Killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.api.killstats.api_helper"
MODULE_PATH2 = "killstats.api.killboard_manager"


class Test_KillboardEndpoints(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()

        cls.user, _ = create_user_from_evecharacter(
            1001,
            permissions=["killstats.basic_access", "killstats.admin_access"],
        )

        cls.user2, _ = create_user_from_evecharacter(
            1002,
            permissions=[
                "killstats.basic_access",
            ],
        )

        cls.killmail = Killmail.objects.get(killmail_id=119303113)

    def test_get_killstats_halls_filter_corporations(self):
        request = MagicMock()
        request.user = self.user
        month = 1
        year = 2023
        entity_id = 0
        entity_type = "corporation"

        with patch(MODULE_PATH + ".get_entities", return_value=[20000001, 10000001]):
            halls = get_killstats_halls(request, month, year, entity_type, entity_id)
            self.assertIsNotNone(halls)
            self.assertIn("shame", halls[0])
            self.assertIn("fame", halls[0])
            self.assertNotIn(10000001, halls[0]["shame"])
            self.assertNotIn(10000001, halls[0]["fame"])

    def test_get_killstats_halls_filter_alliances(self):
        request = MagicMock()
        request.user = self.user
        month = 7
        year = 2024
        entity_id = 0
        entity_type = "alliance"

        halls = get_killstats_halls(request, month, year, entity_type, entity_id)

        self.assertIsNotNone(halls)
        self.assertIn("shame", halls[0])
        self.assertIn("fame", halls[0])
        self.assertNotIn(10000001, halls[0]["shame"])
        self.assertNotIn(10000001, halls[0]["fame"])

    def test_get_killstats_halls_filter_corporations_single(self):
        request = MagicMock()
        request.user = self.user
        month = 7
        year = 2024
        entity_id = 20000001
        entity_type = "corporation"

        halls = get_killstats_halls(request, month, year, entity_type, entity_id)
        self.assertIsNotNone(halls)
        self.assertIn("shame", halls[0])
        self.assertIn("fame", halls[0])
        self.assertNotIn(10000001, halls[0]["shame"])
        self.assertNotIn(10000001, halls[0]["fame"])

    def test_get_killstats_halls_filter_no_enitity(self):
        request = MagicMock()
        request.user = self.user
        month = 7
        year = 2024
        entity_id = 13770000
        entity_type = "corporation"

        halls = get_killstats_halls(request, month, year, entity_type, entity_id)

        self.assertIsNotNone(halls)
        self.assertIn("shame", halls[0])
        self.assertIn("fame", halls[0])
        self.assertNotIn(10000001, halls[0]["shame"])
        self.assertNotIn(10000001, halls[0]["fame"])

    def test_get_character_details_victim_attribute_error(self):
        mains = MagicMock()

        # Konfiguriere den MagicMock so, dass er einen AttributeError auslöst, wenn auf mains.values() zugegriffen wird
        mains.values.side_effect = AttributeError

        character_id, character_name = _get_character_details_victim(
            self.killmail, mains
        )

        self.assertEqual(character_id, 1001)
        self.assertEqual(character_name, "Gneuten")
