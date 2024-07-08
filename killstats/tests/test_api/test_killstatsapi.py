from typing import Optional

from ninja import NinjaAPI

from django.test import TestCase

from app_utils.testing import create_user_from_evecharacter

from killstats.api.killboard import KillboardApiEndpoints
from killstats.tests.test_api.killstasts_api import KillstatsMonth
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all


class ManageApiJournalCharEndpointsTest(TestCase):
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
        cls.api = NinjaAPI()
        cls.manage_api_endpoints = KillboardApiEndpoints(api=cls.api)

    def test_killstats_killboard_api(self):
        # given
        self.client.force_login(self.user)
        url = "/killstats/api/killboard/month/7/year/2024/"
        # when
        response = self.client.get(url)
        # then
        expected_data = KillstatsMonth
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)
