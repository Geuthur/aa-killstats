from unittest.mock import MagicMock, patch

from django.test import TestCase

from app_utils.testing import create_user_from_evecharacter

from killstats.api.killstats.api_helper import get_killstats_halls
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.api.killstats.api_helper"


class ManageApiCorporationEndpointsTest(TestCase):
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

    def test_get_killstats_halls_filter_corporations(self):
        request = MagicMock()
        request.user = self.user
        month = 1
        year = 2023
        entity_id = 0
        entity_type = "corporation"

        with patch(MODULE_PATH + ".get_corporations", return_value=[2001, 10000001]):
            halls = get_killstats_halls(request, month, year, entity_type, entity_id)
            self.assertIsNotNone(halls)
            self.assertIn("shame", halls[0])
            self.assertIn("fame", halls[0])
            self.assertNotIn(10000001, halls[0]["shame"])
            self.assertNotIn(10000001, halls[0]["fame"])

    def test_get_killstats_halls_filter_alliances(self):
        request = MagicMock()
        request.user = self.user
        month = 1
        year = 2023
        entity_id = 0
        entity_type = "alliance"

        with patch(MODULE_PATH + ".get_alliances", return_value=[3001, 10000001]):
            halls = get_killstats_halls(request, month, year, entity_type, entity_id)
            self.assertIsNotNone(halls)
            self.assertIn("shame", halls[0])
            self.assertIn("fame", halls[0])
            self.assertNotIn(10000001, halls[0]["shame"])
            self.assertNotIn(10000001, halls[0]["fame"])
