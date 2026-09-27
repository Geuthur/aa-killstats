"""Unit tests for KillboardApiEndpoints."""

# Standard Library
from unittest.mock import patch

# Third Party
# Django Ninja
from ninja.testing import TestClient

# AA Killstats
from killstats.api import api
from killstats.tests import AuthTestCase
from killstats.tests.testdata.killstats import UserMainFactory

MODULE_PATH = "killstats.api.killstats.killboard"


class TestKillboardApi(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.client = TestClient(api)
        self.user = UserMainFactory()

    @patch(f"{MODULE_PATH}.api_helper")
    def test_get_corporation_killmails_should_return_data(self, mock_api_helper):
        # Test Data
        expected_output = {"killmails": [], "total_kills": 0}
        mock_api_helper.get_killmails_data.return_value = expected_output

        # Test Action
        response = self.client.get(
            "/killmail/month/9/year/2026/corporation/98000001/kills/",
            user=self.user,
        )

        # Expected Result
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_output)
        mock_api_helper.get_killmails_data.assert_called_once()

    @patch(f"{MODULE_PATH}.api_helper")
    def test_get_corporation_halls_should_return_cached_or_computed_data(
        self, mock_api_helper
    ):
        # Test Data
        expected_halls = [{"character_id": 1001, "character_name": "Test Pilot"}]
        mock_api_helper.cache_sytem.return_value = (None, "cache_key_123")
        mock_api_helper.get_killstats_halls.return_value = expected_halls

        # Test Action
        response = self.client.get(
            "/halls/month/9/year/2026/corporation/98000001/",
            user=self.user,
        )

        # Expected Result
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_halls)
        mock_api_helper.get_killstats_halls.assert_called_once()
        mock_api_helper.set_cache_key.assert_called_once_with(
            "cache_key_123", expected_halls
        )
