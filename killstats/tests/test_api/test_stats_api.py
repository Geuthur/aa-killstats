from ninja import NinjaAPI

from django.test import TestCase

from app_utils.testing import create_user_from_evecharacter

from killstats.api.killstats import KillboardApiEndpoints
from killstats.tests.test_api import _stats_api
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.api.killstats.api_helper"


class Test_ApiStatsEndpoints(TestCase):
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

    def test_top_ship_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/ship/top/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)

        # then
        expected_data = _stats_api.top_ship
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/ship/top/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)

        # then
        expected_data = _stats_api.top_ship
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/ship/top/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_worst_ship_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/ship/worst/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.worst_ship
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/ship/worst/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.worst_ship
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/ship/worst/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_top_killer_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/top/killer/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_killer
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/top/killer/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_killer
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/top/killer/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_victim_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/top/victim/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_victim
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/top/victim/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_victim
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/top/victim/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_top_kill_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/top/kill/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_kill
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/top/kill/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_kill
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/top/kill/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_top_loss_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/top/loss/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_loss
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/top/loss/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.top_loss
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/top/loss/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_alltime_killer_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/top/alltime_killer/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.alltime_killer
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/top/alltime_killer/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.alltime_killer
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/top/alltime_killer/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_alltime_victim_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/top/alltime_victim/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.alltime_victim
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Alliance
        url = "/killstats/api/stats/top/alltime_victim/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = _stats_api.alltime_victim
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        # Empty Entry
        url = "/killstats/api/stats/top/alltime_victim/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        expected_data = [{"stats": {}}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

    def test_top_10_api(self):
        # given
        self.client.force_login(self.user)
        self.maxDiff = None

        # Corporation
        url = "/killstats/api/stats/top/10/month/7/year/2024/corporation/0/"
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top 10 Killers")

        # Alliance
        url = "/killstats/api/stats/top/10/month/7/year/2024/alliance/3001/"
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top 10 Killers")

        # Empty Entry
        url = "/killstats/api/stats/top/10/month/7/year/1999/alliance/3001/"
        # when
        response = self.client.get(url)

        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Top 10 Killers")
