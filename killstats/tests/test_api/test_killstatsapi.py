from unittest.mock import patch

from ninja import NinjaAPI

from django.test import TestCase

from allianceauth.eveonline.models import EveCorporationInfo
from app_utils.testing import create_user_from_evecharacter

from killstats.api.killboard import KillboardApiEndpoints
from killstats.tests.test_api._killstasts_api import KillstatsEmpty, KillstatsMonth
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

    def test_killstats_killboard_api_no_entry(self):
        self.maxDiff = None
        # given
        self.client.force_login(self.user)
        url = "/killstats/api/killboard/month/7/year/2020/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = KillstatsEmpty
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_killstats_killboard_api(self):
        self.maxDiff = None
        # given
        self.client.force_login(self.user)
        url = "/killstats/api/killboard/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = KillstatsMonth
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_killstats_killboard_api_single(self):
        self.maxDiff = None
        # given
        self.client.force_login(self.user)
        url = "/killstats/api/killboard/month/7/year/2024/corporation/2001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = KillstatsMonth
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_corporation_admin(self):
        self.client.force_login(self.user2)
        url = "/killstats/api/killboard/corporation/admin/"
        # when
        response = self.client.get(url)
        # then
        excepted_data = [
            {
                "corporation": {
                    "2002": {"corporation_id": 2002, "corporation_name": "Eulenclub"}
                }
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), excepted_data)

    @patch("killstats.api.killboard.killboard.KillstatsAudit.objects.visible_to")
    def test_get_corporation_admin_no_visible(self, mock_visible_to):
        self.client.force_login(self.user2)
        url = "/killstats/api/killboard/corporation/admin/"

        mock_visible_to.return_value = None

        # when
        response = self.client.get(url)
        print(response.json())
        # then
        self.assertContains(response, "Permission Denied", status_code=403)

    @patch("killstats.api.killboard.killboard.KillstatsAudit.objects.visible_to")
    def test_get_corporation_admin_exception(self, mock_visible_to):
        self.client.force_login(self.user)
        url = "/killstats/api/killboard/corporation/admin/"

        corp = EveCorporationInfo.objects.get(corporation_id=2001)

        mock_visible_to.return_value = [corp, "test"]

        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
