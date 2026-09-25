# Standard Library
from io import StringIO
from unittest.mock import Mock, patch

# Django
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

# Alliance Auth
from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)

# Alliance Auth (External Libs)
from eve_sde.models.map import SolarSystem
from eve_sde.models.types import ItemType

# AA Killstats
from killstats.models.general import EveEntity
from killstats.models.killboard import Attacker, Killmail
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tests.testdata.load_allianceauth import load_allianceauth


class TestKillstatsDeleteNpcKillmails(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()

        # Set up a player audited corporation (ID >= 10,000,000)
        cls.player_corp = EveCorporationInfo.objects.create(
            corporation_id=98000001,
            corporation_name="Player Corp",
            corporation_ticker="PC",
            member_count=50,
        )
        cls.player_char = EveCharacter.objects.create(
            character_id=98000010,
            character_name="Player Character",
            corporation_id=cls.player_corp.corporation_id,
            corporation_name=cls.player_corp.corporation_name,
            corporation_ticker=cls.player_corp.corporation_ticker,
        )
        cls.corp_audit = CorporationsAudit.objects.create(
            corporation=cls.player_corp,
            owner=cls.player_char,
        )

        # Set up a player audited alliance (ID >= 10,000,000)
        cls.player_alliance = EveAllianceInfo.objects.create(
            alliance_id=99000001,
            alliance_name="Player Alliance",
            alliance_ticker="PA",
            executor_corp_id=cls.player_corp.corporation_id,
        )
        cls.alliance_audit = AlliancesAudit.objects.create(
            alliance=cls.player_alliance,
            owner=cls.player_char,
        )

        cls.ship = ItemType.objects.first()

    def test_no_killmails_found(self):
        out = StringIO()
        call_command("killstats_delete_npc_killmails", "--yes", stdout=out)
        output = out.getvalue()
        self.assertIn("Found 0 killmail(s)", output)
        self.assertIn("No NPC killmails or NPC audits found to delete", output)

    def test_protected_killmails_not_deleted(self):
        # 1. Killmail where victim is player corp, attacker is NPC corp (1000125)
        km1 = Killmail.objects.create(
            killmail_id=100001,
            victim_corporation_id=self.player_corp.corporation_id,
            victim_alliance_id=self.player_alliance.alliance_id,
            victim_ship=self.ship,
            hash="hash_100001",
        )
        npc_entity, _ = EveEntity.objects.get_or_create(
            id=1000125,
            defaults={"name": "CONCORD", "category": EveEntity.CATEGORY_CORPORATION},
        )
        Attacker.objects.create(
            killmail=km1,
            corporation=npc_entity,
        )

        # 2. Killmail where attacker is player corp, victim is NPC corp (1000035)
        km2 = Killmail.objects.create(
            killmail_id=100002,
            victim_corporation_id=1000035,
            victim_ship=self.ship,
            hash="hash_100002",
        )
        player_entity, _ = EveEntity.objects.get_or_create(
            id=self.player_corp.corporation_id,
            defaults={
                "name": "Player Corp",
                "category": EveEntity.CATEGORY_CORPORATION,
            },
        )
        Attacker.objects.create(
            killmail=km2,
            corporation=player_entity,
        )

        out = StringIO()
        call_command("killstats_delete_npc_killmails", "--yes", stdout=out)
        output = out.getvalue()

        self.assertIn("Found 0 killmail(s)", output)
        self.assertTrue(Killmail.objects.filter(killmail_id=100001).exists())
        self.assertTrue(Killmail.objects.filter(killmail_id=100002).exists())

    def test_npc_killmail_deleted_with_yes_flag(self):
        # NPC killmail completely unconnected to any audit
        km = Killmail.objects.create(
            killmail_id=100003,
            victim_corporation_id=1000035,  # NPC corp
            victim_ship=self.ship,
            hash="hash_100003",
        )
        npc_entity, _ = EveEntity.objects.get_or_create(
            id=1000125,
            defaults={"name": "CONCORD", "category": EveEntity.CATEGORY_CORPORATION},
        )
        Attacker.objects.create(
            killmail=km,
            corporation=npc_entity,
        )

        out = StringIO()
        call_command("killstats_delete_npc_killmails", "--yes", stdout=out)
        output = out.getvalue()

        self.assertIn("Found 1 killmail(s)", output)
        self.assertIn("Successfully deleted 1 NPC killmail(s)", output)
        self.assertFalse(Killmail.objects.filter(killmail_id=100003).exists())
        self.assertFalse(Attacker.objects.filter(killmail_id=100003).exists())

    @patch("builtins.input", return_value="n")
    def test_npc_killmail_cancelled_by_user(self, mock_input):
        Killmail.objects.create(
            killmail_id=100004,
            victim_corporation_id=1000035,
            victim_ship=self.ship,
            hash="hash_100004",
        )

        out = StringIO()
        call_command("killstats_delete_npc_killmails", stdout=out)
        output = out.getvalue()

        self.assertIn("Found 1 killmail(s)", output)
        self.assertIn("Deletion cancelled", output)
        self.assertTrue(Killmail.objects.filter(killmail_id=100004).exists())
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="y")
    def test_npc_killmail_confirmed_by_user(self, mock_input):
        Killmail.objects.create(
            killmail_id=100005,
            victim_corporation_id=1000035,
            victim_ship=self.ship,
            hash="hash_100005",
        )

        out = StringIO()
        call_command("killstats_delete_npc_killmails", stdout=out)
        output = out.getvalue()

        self.assertIn("Found 1 killmail(s)", output)
        self.assertIn("Successfully deleted 1 NPC killmail(s)", output)
        self.assertFalse(Killmail.objects.filter(killmail_id=100005).exists())
        mock_input.assert_called_once()

    def test_dry_run_flag(self):
        Killmail.objects.create(
            killmail_id=100006,
            victim_corporation_id=1000035,
            victim_ship=self.ship,
            hash="hash_100006",
        )

        out = StringIO()
        call_command("killstats_delete_npc_killmails", "--dry-run", stdout=out)
        output = out.getvalue()

        self.assertIn("Found 1 killmail(s)", output)
        self.assertIn("[DRY-RUN] Would delete 1 killmail(s)", output)
        self.assertTrue(Killmail.objects.filter(killmail_id=100006).exists())

    def test_npc_audit_cleanup(self):
        npc_corp, _ = EveCorporationInfo.objects.get_or_create(
            corporation_id=1000125,
            defaults={
                "corporation_name": "CONCORD",
                "corporation_ticker": "CCP",
                "member_count": 100,
            },
        )
        npc_audit = CorporationsAudit.objects.create(
            corporation=npc_corp,
            owner=self.player_char,
        )

        out = StringIO()
        call_command("killstats_delete_npc_killmails", "--yes", stdout=out)
        output = out.getvalue()

        self.assertIn("Found 1 NPC corporation audit(s)", output)
        self.assertIn("Deleted 1 invalid NPC audit(s)", output)
        self.assertFalse(CorporationsAudit.objects.filter(id=npc_audit.id).exists())


class TestKillstatsUpdateSolarSystems(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()

        cls.ship = ItemType.objects.first()
        cls.solar_system = SolarSystem.objects.first()

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def tearDown(self) -> None:
        super().tearDown()
        cache.clear()

    def test_update_solar_systems_none_matching(self):
        # Create killmail with solar_system_id already set
        Killmail.objects.create(
            killmail_id=200001,
            victim_corporation_id=98000001,
            victim_solar_system_id=self.solar_system.id,
            victim_ship=self.ship,
            hash="hash_200001",
        )

        out = StringIO()
        call_command("killstats_update_solar_systems", sleep=0, stdout=out)
        output = out.getvalue()

        self.assertIn("No killmails found with missing solar_system_id", output)

    @patch("requests.get")
    def test_update_solar_systems_success(self, mock_requests_get):
        # Killmail with missing victim_solar_system_id
        km = Killmail.objects.create(
            killmail_id=200002,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_region_id=None,
            victim_ship=self.ship,
            hash="hash_200002",
        )

        # Mock ESI response returning solar_system_id
        mock_response = patch("requests.Response").start()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "killmail_id": 200002,
            "solar_system_id": self.solar_system.id,
        }
        mock_requests_get.return_value = mock_response

        out = StringIO()
        call_command("killstats_update_solar_systems", sleep=0, stdout=out)
        output = out.getvalue()

        self.assertIn("Found 1 killmail(s) matching criteria", output)
        self.assertIn("Updated: 1", output)

        km.refresh_from_db()
        self.assertEqual(km.victim_solar_system_id, self.solar_system.id)
        self.assertIsNotNone(km.victim_region_id)
        self.assertEqual(km.victim_region_id, self.solar_system.constellation.region_id)

    @patch("requests.get")
    def test_update_solar_systems_dry_run(self, mock_requests_get):
        km = Killmail.objects.create(
            killmail_id=200003,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200003",
        )

        out = StringIO()
        call_command("killstats_update_solar_systems", "--dry-run", sleep=0, stdout=out)
        output = out.getvalue()

        self.assertIn("[DRY-RUN] Would check and update 1 killmail(s)", output)
        mock_requests_get.assert_not_called()

        km.refresh_from_db()
        self.assertIsNone(km.victim_solar_system_id)

    @patch("requests.get")
    def test_update_solar_systems_failed_fetch(self, mock_requests_get):
        km = Killmail.objects.create(
            killmail_id=200004,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200004",
        )

        # Mock ESI 404 response
        mock_response = patch("requests.Response").start()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        out = StringIO()
        call_command("killstats_update_solar_systems", sleep=0, stdout=out)
        output = out.getvalue()

        self.assertIn("Failed (could not fetch): 1", output)
        km.refresh_from_db()
        self.assertIsNone(km.victim_solar_system_id)

    @patch("requests.get")
    def test_update_solar_systems_missing_only_flag(self, mock_requests_get):
        km_with_system = Killmail.objects.create(
            killmail_id=200005,
            victim_corporation_id=98000001,
            victim_solar_system_id=self.solar_system.id,
            victim_ship=self.ship,
            hash="hash_200005",
        )
        km_without_system = Killmail.objects.create(
            killmail_id=200006,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200006",
        )

        mock_response = patch("requests.Response").start()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "killmail_id": 200006,
            "solar_system_id": self.solar_system.id,
        }
        mock_requests_get.return_value = mock_response

        out = StringIO()
        call_command(
            "killstats_update_solar_systems", "--missing-only", sleep=0, stdout=out
        )
        output = out.getvalue()

        self.assertIn(
            "Mode: Checking ONLY killmails with missing solar_system_id", output
        )
        self.assertIn("Found 1 killmail(s) matching criteria", output)
        self.assertIn("Updated: 1", output)

        km_without_system.refresh_from_db()
        self.assertEqual(km_without_system.victim_solar_system_id, self.solar_system.id)
        km_with_system.refresh_from_db()
        self.assertEqual(km_with_system.victim_solar_system_id, self.solar_system.id)

    @patch("requests.get")
    def test_update_solar_systems_limit(self, mock_requests_get):
        Killmail.objects.create(
            killmail_id=200007,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200007",
        )
        Killmail.objects.create(
            killmail_id=200008,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200008",
        )

        mock_response = patch("requests.Response").start()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "killmail_id": 200008,
            "solar_system_id": self.solar_system.id,
        }
        mock_requests_get.return_value = mock_response

        out = StringIO()
        call_command(
            "killstats_update_solar_systems", "--limit", "1", sleep=0, stdout=out
        )
        output = out.getvalue()

        self.assertIn("Found 2 killmail(s) matching criteria (limited to 1)", output)
        self.assertIn("Updated: 1", output)

    @patch("requests.get")
    def test_update_solar_systems_zero_solar_system_id(self, mock_requests_get):
        km_zero = Killmail.objects.create(
            killmail_id=200009,
            victim_corporation_id=98000001,
            victim_solar_system_id=0,
            victim_ship=self.ship,
            hash="hash_200009",
        )

        mock_response = patch("requests.Response").start()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "killmail_id": 200009,
            "solar_system_id": self.solar_system.id,
        }
        mock_requests_get.return_value = mock_response

        out = StringIO()
        call_command("killstats_update_solar_systems", "-m", sleep=0, stdout=out)
        output = out.getvalue()

        self.assertIn("Found 1 killmail(s) matching criteria", output)
        self.assertIn("Updated: 1", output)

        km_zero.refresh_from_db()
        self.assertEqual(km_zero.victim_solar_system_id, self.solar_system.id)

    @patch("requests.get")
    def test_update_solar_systems_zkb_fallback(self, mock_requests_get):
        km = Killmail.objects.create(
            killmail_id=200010,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200010",
        )

        resp_esi = Mock(status_code=404)
        resp_zkb = Mock(
            status_code=200,
            json=Mock(return_value=[{"solar_system_id": self.solar_system.id}]),
        )
        mock_requests_get.side_effect = [resp_esi, resp_zkb]

        out = StringIO()
        call_command("killstats_update_solar_systems", sleep=0, stdout=out)
        output = out.getvalue()

        self.assertIn("Updated: 1", output)
        km.refresh_from_db()
        self.assertEqual(km.victim_solar_system_id, self.solar_system.id)

    @patch("requests.get")
    def test_update_solar_systems_rate_limit_stops_early(self, mock_requests_get):
        Killmail.objects.create(
            killmail_id=200011,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200011",
        )

        # Token bucket is at 550, which is below default reserve of 600
        cache.set("esi:bucket:killmail", 550, 900)

        out = StringIO()
        call_command("killstats_update_solar_systems", sleep=0, stdout=out)
        output = out.getvalue()

        self.assertIn("[RATE-LIMIT]", output)
        self.assertIn("at or below reserve (600)", output)
        self.assertIn("Stopped by rate limit reserve: Yes", output)
        mock_requests_get.assert_not_called()

    @patch("requests.get")
    def test_update_solar_systems_custom_min_reserve(self, mock_requests_get):
        km = Killmail.objects.create(
            killmail_id=200012,
            victim_corporation_id=98000001,
            victim_solar_system_id=None,
            victim_ship=self.ship,
            hash="hash_200012",
        )

        # Token bucket is at 300
        cache.set("esi:bucket:killmail", 300, 900)

        mock_response = patch("requests.Response").start()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "killmail_id": 200012,
            "solar_system_id": self.solar_system.id,
        }
        mock_requests_get.return_value = mock_response

        # With --min-reserve 200, 300 is above reserve -> should process
        out = StringIO()
        call_command(
            "killstats_update_solar_systems",
            "--min-reserve",
            "200",
            sleep=0,
            stdout=out,
        )
        output = out.getvalue()

        self.assertIn("Updated: 1", output)
        self.assertIn("Stopped by rate limit reserve: No", output)
        km.refresh_from_db()
        self.assertEqual(km.victim_solar_system_id, self.solar_system.id)
