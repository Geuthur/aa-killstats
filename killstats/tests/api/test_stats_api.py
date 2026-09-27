"""Unit tests for KillboardStatsApiEndpoints."""

# Standard Library
from unittest.mock import patch

# Third Party
# Django Ninja
from ninja.testing import TestClient

# AA Killstats
from killstats.api import api
from killstats.tests import AuthTestCase
from killstats.tests.testdata.killstats import UserMainFactory

MODULE_PATH = "killstats.api.killstats.stats"


class TestKillboardStatsApi(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.client = TestClient(api)
        self.user = UserMainFactory()

    @patch(f"{MODULE_PATH}.api_helper")
    def test_get_top_10_api_should_render_modal(self, mock_api_helper):
        # Test Data
        mock_api_helper.cache_sytem.return_value = (None, "cache_key_top10")
        mock_api_helper.get_top_10.return_value = []

        # Test Action
        response = self.client.get(
            "/stats/top/10/month/9/year/2026/corporation/98000001/",
            user=self.user,
        )

        # Expected Result
        self.assertEqual(response.status_code, 200)
        mock_api_helper.get_top_10.assert_called_once()
        mock_api_helper.set_cache_key.assert_called_once_with(
            "cache_key_top10", {"top10": []}
        )

    @patch(f"{MODULE_PATH}.api_helper")
    def test_get_all_stats_should_return_stats_dict(self, mock_api_helper):
        # Test Data
        mock_api_helper.cache_sytem.return_value = (None, "cache_key_all_stats")
        mock_api_helper.get_entities.return_value = [98000001]

        # Test Action
        response = self.client.get(
            "/stats/all/month/9/year/2026/corporation/98000001/",
            user=self.user,
        )

        # Expected Result
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stats", data)
        self.assertIn("alltime_killer", data["stats"])
        self.assertIn("top_ship", data["stats"])
        mock_api_helper.set_cache_key.assert_called_once()
