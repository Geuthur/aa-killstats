"""Unit tests for api.killstats.api_helper module."""

# Standard Library
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

# Third Party
from evesde_factory.allianceauth import (
    EveAllianceInfoFactory,
    EveCharacterFactory,
    EveCorporationInfoFactory,
)
from evesde_factory.eve_sde import ItemTypeFactory

# Django
from django.core.cache import cache
from django.test import RequestFactory

# AA Killstats
from killstats.api.killstats import api_helper
from killstats.models import Attacker, Killmail
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tests import AuthTestCase
from killstats.tests.testdata.killstats import (
    AlliancesAuditFactory,
    AttackerFactory,
    CorporationsAuditFactory,
    EveEntityFactory,
    KillmailFactory,
    UserMainFactory,
)

MODULE_PATH = "killstats.api.killstats.api_helper"


class TestApiHelper(AuthTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_set_cache_key_should_return_false_when_key_empty(self):
        # Test Action
        result = api_helper.set_cache_key("", "data")

        # Expected Result
        self.assertFalse(result)

    def test_set_cache_key_should_store_data_and_return_true(self):
        # Test Action
        result = api_helper.set_cache_key("test_key", {"foo": "bar"}, timeout=5)

        # Expected Result
        self.assertTrue(result)
        self.assertEqual(cache.get("test_key"), {"foo": "bar"})

    def test_cache_sytem_should_return_hit_when_cached(self):
        # Test Data
        request = self.request
        request.user = self.user
        cache.set("overview_123", {"status": "ok"})

        # Test Action
        output, cache_key = api_helper.cache_sytem(request, "overview", 123)

        # Expected Result
        self.assertEqual(output, {"status": "ok"})
        self.assertIsNone(cache_key)

    def test_cache_sytem_should_return_miss_key_when_not_cached(self):
        # Test Data
        request = self.request
        request.user = self.user

        # Test Action
        output, cache_key = api_helper.cache_sytem(request, "overview", 123)

        # Expected Result
        self.assertIsNone(output)
        self.assertEqual(cache_key, "overview_123")

    def test_get_unique_id_should_return_entity_id_when_not_zero(self):
        # Test Data
        request = self.request
        request.user = self.user

        # Test Action & Expected Result
        self.assertEqual(api_helper.get_unique_id(request, 456), 456)

    def test_get_unique_id_should_hash_entities_when_entity_id_is_zero(self):
        # Test Data
        corp = EveCorporationInfoFactory()
        CorporationsAuditFactory(corporation=corp)
        request = self.request
        request.user = self.user

        # Test Action
        with (
            patch(
                f"{MODULE_PATH}.get_corporations", return_value=[corp.corporation_id]
            ),
            patch(f"{MODULE_PATH}.get_alliances", return_value=[]),
        ):
            unique_id = api_helper.get_unique_id(request, 0)

        # Expected Result
        self.assertIsInstance(unique_id, str)
        self.assertEqual(len(unique_id), 32)  # md5 hex length

    def test_get_entities_should_return_single_entity_id_when_nonzero(self):
        # Test Data
        request = self.request
        request.user = self.user

        # Test Action & Expected Result
        self.assertEqual(api_helper.get_entities(request, "corporation", 1001), [1001])

    def test_get_entities_should_return_alliances_when_type_alliance_and_id_zero(self):
        # Test Data
        request = self.request
        request.user = self.user

        # Test Action
        with patch(f"{MODULE_PATH}.get_alliances", return_value=[99001, 99002]):
            entities = api_helper.get_entities(request, "alliance", 0)

        # Expected Result
        self.assertEqual(entities, [99001, 99002])

    def test_get_entities_should_return_corps_when_type_corp_and_id_zero(self):
        # Test Data
        request = self.request
        request.user = self.user

        # Test Action
        with patch(f"{MODULE_PATH}.get_corporations", return_value=[98001]):
            entities = api_helper.get_entities(request, "corporation", 0)

        # Expected Result
        self.assertEqual(entities, [98001])

    def test_get_killmails_data_should_return_paginated_kills(self):
        # Test Data
        corp_id = 98001
        km_date = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)
        km = KillmailFactory(
            killmail_date=km_date,
            victim_total_value=500000,
        )
        AttackerFactory(killmail=km, corporation__id=corp_id)

        request = self.request
        request.GET = {
            "start": "0",
            "length": "10",
            "draw": "1",
            "order[0][column]": "0",
            "order[0][dir]": "desc",
        }
        request.user = self.user

        # Test Action
        result = api_helper.get_killmails_data(
            request,
            month=9,
            year=2026,
            entity_type="corporation",
            entity_id=corp_id,
            mode="kills",
        )

        # Expected Result
        self.assertEqual(result["draw"], 1)
        self.assertEqual(result["recordsTotal"], 1)
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["killmail_id"], km.killmail_id)

    def test_get_killmails_data_should_filter_by_search_value(self):
        # Test Data
        corp_id = 98002
        km_date = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)
        victim_entity = EveEntityFactory(name="Target Pilot")
        km = KillmailFactory(
            killmail_date=km_date,
            victim=victim_entity,
            victim_total_value=1000000,
        )
        AttackerFactory(killmail=km, corporation__id=corp_id)

        request = self.request
        request.GET = {
            "start": "0",
            "length": "10",
            "draw": "1",
            "search[value]": "Target Pilot",
        }
        request.user = self.user

        # Test Action
        result = api_helper.get_killmails_data(
            request,
            month=9,
            year=2026,
            entity_type="corporation",
            entity_id=corp_id,
            mode="kills",
        )

        # Expected Result
        self.assertEqual(result["recordsFiltered"], 1)
        self.assertEqual(len(result["data"]), 1)

    def test_get_killstats_halls_should_return_shame_and_fame(self):
        # Test Data
        corp_id = 98003
        km_date = datetime(2026, 9, 20, 14, 0, 0, tzinfo=timezone.utc)

        # Loss (shame)
        victim = EveEntityFactory(name="Unfortunate Victim")
        km_loss = KillmailFactory(
            killmail_date=km_date,
            victim=victim,
            victim_corporation_id=corp_id,
            victim_total_value=50000000,
        )

        # Kill (fame)
        attacker_char = EveEntityFactory(name="Hero Pilot")
        km_kill = KillmailFactory(
            killmail_date=km_date,
            victim_total_value=100000000,
        )
        AttackerFactory(
            killmail=km_kill,
            character=attacker_char,
            corporation__id=corp_id,
        )

        request = self.request
        request.GET = {}
        request.user = self.user

        mock_main = SimpleNamespace(character_name="Main Hero")
        mock_alt = SimpleNamespace(character_id=attacker_char.id)
        mock_mains = {
            99999: {"main": mock_main, "alts": [mock_alt]},
        }

        # Test Action
        with patch.object(
            api_helper.AccountManager,
            "get_mains_alts",
            return_value=(mock_mains, {}),
        ):
            halls = api_helper.get_killstats_halls(
                request,
                month=9,
                year=2026,
                entity_type="corporation",
                entity_id=corp_id,
            )

        # Expected Result
        self.assertEqual(len(halls), 1)
        shame = halls[0]["shame"]
        fame = halls[0]["fame"]
        self.assertEqual(len(shame), 1)
        self.assertEqual(shame[0]["killmail_id"], km_loss.killmail_id)
        self.assertEqual(len(fame), 1)
        self.assertEqual(fame[0]["killmail_id"], km_kill.killmail_id)
        self.assertIn("Main Hero", fame[0]["character_name"])

    def test_get_top_10_should_return_empty_when_no_kills(self):
        # Test Data
        request = self.request
        request.GET = {}
        request.user = self.user

        # Test Action
        with patch.object(
            api_helper.AccountManager,
            "get_mains_alts",
            return_value=({}, {}),
        ):
            top_10 = api_helper.get_top_10(
                request,
                month=1,
                year=2020,
                entity_type="corporation",
                entity_id=98999,
            )

        # Expected Result
        self.assertEqual(top_10, {})

    def test_get_top_10_should_return_ranked_characters(self):
        # Test Data
        corp_id = 98004
        km_date = datetime(2026, 9, 21, 10, 0, 0, tzinfo=timezone.utc)
        char1 = EveEntityFactory(name="Ace Pilot")

        km1 = KillmailFactory(killmail_date=km_date)
        AttackerFactory(killmail=km1, character=char1, corporation__id=corp_id)
        km2 = KillmailFactory(killmail_date=km_date)
        AttackerFactory(killmail=km2, character=char1, corporation__id=corp_id)

        request = self.request
        request.GET = {}
        request.user = self.user

        mock_main = SimpleNamespace(character_name="Main Ace")
        mock_alt = SimpleNamespace(character_id=char1.id)
        mock_mains = {
            88888: {"main": mock_main, "alts": [mock_alt]},
        }

        # Test Action
        with patch.object(
            api_helper.AccountManager,
            "get_mains_alts",
            return_value=(mock_mains, {}),
        ):
            top_10 = api_helper.get_top_10(
                request,
                month=9,
                year=2026,
                entity_type="corporation",
                entity_id=corp_id,
            )

        # Expected Result
        self.assertEqual(len(top_10), 1)
        self.assertEqual(top_10[0]["character_id"], char1.id)
        self.assertEqual(top_10[0]["kill_count"], 2)
        self.assertIn("Main Ace", top_10[0]["character__name"])
