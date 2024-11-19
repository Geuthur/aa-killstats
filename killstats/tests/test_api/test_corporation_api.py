from unittest.mock import patch

from ninja import NinjaAPI

from django.core.cache import cache
from django.test import TestCase

from allianceauth.eveonline.models import EveCorporationInfo
from app_utils.testing import create_user_from_evecharacter

from killstats.api.killstats import KillboardApiEndpoints
from killstats.tests.test_api import _killstasts_api
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.api.killstats.api_helper"


class Test_CorporationEndpoints(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()
        cache.clear()

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

    def test_corp_halls_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Hall of Fame
        url = "/killstats/api/halls/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)

        # then
        expected_data = _killstasts_api.Killstats_Halls_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Cached Hall of Fame
        url = "/killstats/api/halls/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)

        # then
        expected_data = _killstasts_api.Killstats_Halls_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_corp_halls_api_single(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Hall of Fame
        url = "/killstats/api/halls/month/7/year/2024/corporation/20000001/"
        # when
        response = self.client.get(url)

        # then
        expected_data = _killstasts_api.Killstats_Halls_Single
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_killmail_api(self):
        # given
        self.client.force_login(self.user)

        url = "/killstats/api/killmail/month/7/year/2024/corporation/30000001/kills/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _killstasts_api.Killstats_Kills_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        url = "/killstats/api/killmail/month/7/year/2024/corporation/0/losses/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _killstasts_api.Killstats_Losses_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_killmail_api_search(self):
        # given
        self.client.force_login(self.user)

        url = "/killstats/api/killmail/month/7/year/2024/corporation/20000001/losses/?search[value]=Gneuten"
        expected_data = _killstasts_api.Killstats_Search_Entry

        # when
        response = self.client.get(url)

        # then
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
                    "20000002": {
                        "corporation_id": 20000002,
                        "corporation_name": "Eulenclub",
                    }
                }
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), excepted_data)

    @patch("killstats.api.killstats.admin.CorporationsAudit.objects.visible_to")
    def test_get_corporation_admin_no_visible(self, mock_visible_to):
        self.client.force_login(self.user2)
        url = "/killstats/api/killboard/corporation/admin/"

        mock_visible_to.return_value = None

        # when
        response = self.client.get(url)
        # then
        self.assertContains(response, "Permission Denied", status_code=403)

    @patch("killstats.api.killstats.admin.CorporationsAudit.objects.visible_to")
    def test_get_corporation_admin_exception(self, mock_visible_to):
        self.client.force_login(self.user)
        url = "/killstats/api/killboard/corporation/admin/"

        corp = EveCorporationInfo.objects.get(corporation_id=20000001)

        mock_visible_to.return_value = [corp, "test"]

        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
