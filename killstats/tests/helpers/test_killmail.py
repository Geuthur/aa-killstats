# Standard Library
from datetime import timedelta
from unittest.mock import Mock, patch

# Django
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone

# AA Killstats
from killstats import __title__
from killstats.constants import LAST_REQUEST_KEY, RETRY_AFTER_KEY
from killstats.helpers.killmailbody import KillmailBody
from killstats.tests import NoSocketsTestCase

MODULE_PATH = "killstats.helpers.killmailbody"


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TestKillmailHelper(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        cache.clear()

    @patch(MODULE_PATH + ".time.sleep")
    def test_should_wait_for_retry_after(self, mocked_sleep):
        # Test Data
        now = timezone.now()
        retry_after = now + timedelta(seconds=0.75)
        cache.set(RETRY_AFTER_KEY, retry_after)

        # Test Action
        with patch(MODULE_PATH + ".timezone.now", return_value=now):
            result = KillmailBody._rate_limit()

        # Expected Result
        self.assertTrue(result)
        mocked_sleep.assert_called_once_with(0.75)

    @patch(MODULE_PATH + ".time.sleep")
    def test_should_wait_when_within_timeout(self, mocked_sleep):
        # Test Data
        now = timezone.now()
        last_request = now - timedelta(seconds=0.2)
        cache.set(LAST_REQUEST_KEY, last_request.isoformat())
        # Test Action
        with (
            patch(MODULE_PATH + ".KILLSTATS_MAX_ZKB_PER_SEC", 2),
            patch(MODULE_PATH + ".KILLSTATS_ZKB_RATE_TIMEOUT", 0.5),
            patch(MODULE_PATH + ".timezone.now", return_value=now),
        ):
            result = KillmailBody._rate_limit()

        # Expected Result
        self.assertTrue(result)
        mocked_sleep.assert_called_once_with(0.3)

    @patch(MODULE_PATH + ".time.sleep")
    def test_should_skip_when_wait_exceeds_timeout(self, mocked_sleep):
        # Test Data
        now = timezone.now()
        last_request = now - timedelta(seconds=0.1)
        cache.set(LAST_REQUEST_KEY, last_request.isoformat())
        # Test Action
        with (
            patch(MODULE_PATH + ".KILLSTATS_MAX_ZKB_PER_SEC", 2),
            patch(MODULE_PATH + ".KILLSTATS_ZKB_RATE_TIMEOUT", 0.2),
            patch(MODULE_PATH + ".timezone.now", return_value=now),
        ):
            result = KillmailBody._rate_limit()

        # Expected Result
        self.assertFalse(result)
        mocked_sleep.assert_not_called()

    @patch(MODULE_PATH + ".requests.get")
    @patch.object(KillmailBody, "_rate_limit", return_value=False)
    def test_should_return_none_from_r2z2_when_rate_limited(
        self, _mock_rate_limit, mock_requests_get
    ):
        # Test Action
        result = KillmailBody.get_sequence()

        # Expected Result
        self.assertIsNone(result)
        mock_requests_get.assert_not_called()

    @patch(MODULE_PATH + ".requests.get")
    @patch.object(KillmailBody, "_too_many_requests_delay", return_value=False)
    @patch.object(KillmailBody, "_rate_limit", return_value=True)
    def test_should_return_sequence_from_r2z2(
        self, _mock_rate_limit, _mock_delay, mock_requests_get
    ):
        # Test Data
        response = Mock()
        response.json.return_value = {"sequence": 123456}
        mock_requests_get.return_value = response

        # Test Action
        result = KillmailBody.get_sequence()

        # Expected Result
        self.assertEqual(result, 123456)
        self.assertIsNotNone(cache.get(LAST_REQUEST_KEY))
        mock_requests_get.assert_called_once()

    @patch(MODULE_PATH + ".requests.get")
    @patch.object(KillmailBody, "_too_many_requests_delay", return_value=True)
    @patch.object(KillmailBody, "_rate_limit", return_value=True)
    def test_should_return_none_from_r2z2_on_too_many_requests(
        self, _mock_rate_limit, _mock_delay, mock_requests_get
    ):
        # Test Data
        response = Mock()
        response.json.return_value = {"sequence": 123456}
        mock_requests_get.return_value = response

        # Test Action
        result = KillmailBody.get_sequence()

        # Expected Result
        self.assertIsNone(result)

    @patch(MODULE_PATH + ".requests.get")
    @patch.object(KillmailBody, "_rate_limit", return_value=True)
    def test_should_return_none_from_r2z2_sequence_on_worker_shutdown(
        self, _mock_rate_limit, mock_requests_get
    ):
        # Test Data
        cache.set(f"{__title__.upper()}_WORKER_SHUTDOWN", True)
        # Test Action
        result = KillmailBody.create_from_sequence(123456)

        # Expected Result
        self.assertIsNone(result)
        mock_requests_get.assert_not_called()

    @patch(MODULE_PATH + ".requests.get")
    @patch.object(KillmailBody, "_create_from_dict")
    @patch.object(KillmailBody, "_too_many_requests_delay", return_value=False)
    @patch.object(KillmailBody, "_rate_limit", return_value=True)
    def test_should_return_killmail_from_r2z2_sequence(
        self,
        _mock_rate_limit,
        _mock_delay,
        mock_create_from_dict,
        mock_requests_get,
    ):
        # Test Data
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"killmail_id": 999999}
        mock_requests_get.return_value = response

        expected_killmail = Mock()
        mock_create_from_dict.return_value = expected_killmail
        # Test Action
        result = KillmailBody.create_from_sequence(123456)

        # Expected Result
        self.assertEqual(result, expected_killmail)
        mock_create_from_dict.assert_called_once_with({"killmail_id": 999999})
        self.assertIsNotNone(cache.get(LAST_REQUEST_KEY))
