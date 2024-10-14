from unittest.mock import patch

from ninja import NinjaAPI

from django.test import TestCase

from allianceauth.eveonline.models import EveAllianceInfo
from app_utils.testing import create_user_from_evecharacter

from killstats.api.killboard import KillboardAllianceApiEndpoints
from killstats.tests.test_api import _alliance_api
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all


class ManageApiAllianceEndpointsTest(TestCase):
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
        cls.manage_api_endpoints = KillboardAllianceApiEndpoints(api=cls.api)

    def test_killstats_killboard_api_no_entry(self):
        self.maxDiff = None
        # given
        self.client.force_login(self.user)
        url = "/killstats/api/stats/month/7/year/2020/alliance/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _alliance_api.Killstats_Stats
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_killstats_killboard_api(self):
        # given
        self.client.force_login(self.user)

        # Stats - Main
        url = "/killstats/api/stats/month/7/year/2024/alliance/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _alliance_api.Killstats_Stats_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Halls of Fame/Shame - Main
        url = "/killstats/api/halls/month/7/year/2024/alliance/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _alliance_api.Killstats_Halls_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_killmail_api(self):
        # given
        self.client.force_login(self.user)

        url = "/killstats/api/killmail/month/7/year/2024/alliance/3001/kills/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _alliance_api.Killstats_Kills_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        url = "/killstats/api/killmail/month/7/year/2024/alliance/0/losses/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _alliance_api.Killstats_Losses_Entry
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_killstats_killboard_api_single(self):
        # given
        self.client.force_login(self.user)

        # Stats - Single
        url = "/killstats/api/stats/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _alliance_api.Killstats_Stats_Single
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Halls of Fame/Shame - Single
        url = "/killstats/api/halls/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _alliance_api.Killstats_Halls_Single
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_get_alliance_admin(self):
        self.client.force_login(self.user2)
        url = "/killstats/api/killboard/alliance/admin/"
        # when
        response = self.client.get(url)
        # then
        excepted_data = [
            {
                "alliance": {
                    "3001": {"alliance_id": 3001, "alliance_name": "Voices of War"}
                }
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), excepted_data)

    @patch(
        "killstats.api.killboard.alliance.killboard.AlliancesAudit.objects.visible_to"
    )
    def test_get_alliance_admin_no_visible(self, mock_visible_to):
        self.client.force_login(self.user2)
        url = "/killstats/api/killboard/alliance/admin/"

        mock_visible_to.return_value = None

        # when
        response = self.client.get(url)
        # then
        self.assertContains(response, "Permission Denied", status_code=403)

    @patch(
        "killstats.api.killboard.alliance.killboard.AlliancesAudit.objects.visible_to"
    )
    def test_get_alliance_admin_exception(self, mock_visible_to):
        self.client.force_login(self.user)
        url = "/killstats/api/killboard/alliance/admin/"

        corp = EveAllianceInfo.objects.get(alliance_id=3001)

        mock_visible_to.return_value = [corp, "test"]

        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
