"""Unit tests for helpers.core module."""

# Standard Library
import datetime as dt
import json
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

# AA Killstats
from killstats.helpers.core import (
    JSONDateTimeDecoder,
    JSONDateTimeEncoder,
    get_redis_client,
)
from killstats.tests import AuthTestCase

MODULE_PATH = "killstats.helpers.core"


class TestCoreHelpers(AuthTestCase):
    def test_get_redis_client_should_return_django_redis_connection(self):
        # Test Data
        mock_conn = Mock()

        # Test Action
        with patch(
            f"{MODULE_PATH}.django_redis.get_redis_connection",
            return_value=mock_conn,
        ) as mock_get_conn:
            client = get_redis_client()

        # Expected Result
        self.assertEqual(client, mock_conn)
        mock_get_conn.assert_called_once_with("default")

    def test_get_redis_client_should_fallback_to_caches_on_attribute_error(
        self,
    ):
        # Test Data
        mock_master_client = Mock()
        mock_cache = Mock()
        mock_cache.get_master_client.return_value = mock_master_client

        # Test Action
        with (
            patch(
                f"{MODULE_PATH}.django_redis.get_redis_connection",
                side_effect=AttributeError,
            ),
            patch(f"{MODULE_PATH}.caches", {"default": mock_cache}),
        ):
            client = get_redis_client()

        # Expected Result
        self.assertEqual(client, mock_master_client)
        mock_cache.get_master_client.assert_called_once()

    def test_json_datetime_encoder_should_encode_aware_datetime(self):
        # Test Data
        now = dt.datetime(2026, 9, 27, 12, 30, 45, 123456, tzinfo=ZoneInfo("UTC"))

        # Test Action
        encoded_json = json.dumps({"date": now}, cls=JSONDateTimeEncoder)
        data = json.loads(encoded_json)

        # Expected Result
        self.assertEqual(data["date"]["__type__"], "datetime")
        self.assertEqual(data["date"]["year"], 2026)
        self.assertEqual(data["date"]["month"], 9)
        self.assertEqual(data["date"]["day"], 27)
        self.assertEqual(data["date"]["hour"], 12)
        self.assertEqual(data["date"]["minute"], 30)
        self.assertEqual(data["date"]["second"], 45)
        self.assertEqual(data["date"]["microsecond"], 123456)
        self.assertEqual(data["date"]["tz"], ["UTC", None])

    def test_json_datetime_encoder_should_encode_naive_datetime(self):
        # Test Data
        naive = dt.datetime(2026, 9, 27, 15, 0, 0)

        # Test Action
        encoded_json = json.dumps({"date": naive}, cls=JSONDateTimeEncoder)
        data = json.loads(encoded_json)

        # Expected Result
        self.assertEqual(data["date"]["__type__"], "datetime")
        self.assertIsNone(data["date"]["tz"][0])
        self.assertIsNone(data["date"]["tz"][1])

    def test_json_datetime_encoder_should_raise_type_error_for_unknown_object(
        self,
    ):
        # Test Data
        class Unserializable:
            pass

        # Test Action & Expected Result
        with self.assertRaises(TypeError):
            json.dumps({"obj": Unserializable()}, cls=JSONDateTimeEncoder)

    def test_json_datetime_decoder_should_decode_datetime(self):
        # Test Data
        now = dt.datetime(2026, 9, 27, 12, 30, 45, tzinfo=ZoneInfo("UTC"))
        encoded = json.dumps({"date": now}, cls=JSONDateTimeEncoder)

        # Test Action
        decoded = json.loads(encoded, cls=JSONDateTimeDecoder)

        # Expected Result
        self.assertEqual(decoded["date"], now)

    def test_json_datetime_decoder_should_preserve_dict_without_type(self):
        # Test Data
        json_str = json.dumps({"key": "value", "num": 42})

        # Test Action
        decoded = json.loads(json_str, cls=JSONDateTimeDecoder)

        # Expected Result
        self.assertEqual(decoded, {"key": "value", "num": 42})

    def test_json_datetime_decoder_should_handle_invalid_datetime_gracefully(
        self,
    ):
        # Test Data: Invalid month (13)
        corrupted_json = json.dumps(
            {
                "date": {
                    "__type__": "datetime",
                    "year": 2026,
                    "month": 13,
                    "day": 1,
                    "hour": 0,
                    "minute": 0,
                    "second": 0,
                    "microsecond": 0,
                    "tz": ["UTC", 0],
                }
            }
        )

        # Test Action
        decoded = json.loads(corrupted_json, cls=JSONDateTimeDecoder)

        # Expected Result: Fallback to dictionary with __type__ restored
        self.assertIn("date", decoded)
        self.assertEqual(decoded["date"]["__type__"], "datetime")
