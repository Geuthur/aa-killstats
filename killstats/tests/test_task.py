# Standard Library
from unittest.mock import Mock, patch

# Django
from django.core.cache import cache
from django.utils import timezone

# AA Killstats
from killstats import __title__
from killstats.tasks import (
    check_and_import_alliance_killmails_task,
    check_and_import_corporation_killmails_task,
    check_missing_killmails,
    fetch_solar_system_id_for_killmail,
    import_missing_killmails_from_zkb,
    run_tracker_alliance,
    run_tracker_corporation,
    run_tracker_missing_data,
    run_zkb_r2z2,
    update_missing_solar_systems_task,
)
from killstats.tests import NoSocketsTestCase

HELPER_PATH = "killstats.helpers.killmail"
HELPER_TASKS_PATH = "killstats.helpers.tasks"
MODULE_PATH = "killstats.tasks"


class TestTasks(NoSocketsTestCase):
    def setUp(self) -> None:
        cache.clear()

    @patch(MODULE_PATH + ".logger.error")
    @patch(HELPER_PATH + ".KillmailBody.get_sequence_from_r2z2")
    def test_run_zkb_r2z2_handles_sequence_exception(
        self, mock_get_sequence, mock_logger_error
    ):
        mock_get_sequence.side_effect = Exception("boom")

        run_zkb_r2z2()

        mock_logger_error.assert_called_once()

    @patch(HELPER_PATH + ".KillmailBody.create_from_r2z2_sequence")
    @patch(HELPER_PATH + ".KillmailBody.get_sequence_from_r2z2", return_value=None)
    def test_run_zkb_r2z2_returns_when_no_sequence(
        self, _mock_get_sequence, mock_create_from_sequence
    ):
        run_zkb_r2z2()

        mock_create_from_sequence.assert_not_called()

    @patch(MODULE_PATH + ".run_tracker_alliance.delay")
    @patch(MODULE_PATH + ".run_tracker_corporation.delay")
    @patch(MODULE_PATH + ".AlliancesAudit.objects.all")
    @patch(MODULE_PATH + ".CorporationsAudit.objects.all")
    @patch(HELPER_PATH + ".KillmailBody.create_from_r2z2_sequence")
    @patch(HELPER_PATH + ".KillmailBody.get_sequence_from_r2z2", return_value=100)
    def test_run_zkb_r2z2_processes_and_dispatches_trackers(
        self,
        _mock_get_sequence,
        mock_create_from_sequence,
        mock_corps_all,
        mock_allys_all,
        mock_run_tracker_corp_delay,
        mock_run_tracker_ally_delay,
    ):
        corporation_audit = Mock()
        corporation_audit.corporation.corporation_id = 2001
        mock_corps_all.return_value = [corporation_audit]

        alliance_audit = Mock()
        alliance_audit.alliance.alliance_id = 3001
        mock_allys_all.return_value = [alliance_audit]

        killmail = Mock()
        killmail.id = 123456
        killmail.save = Mock()

        mock_create_from_sequence.side_effect = [killmail, None]

        run_zkb_r2z2()

        killmail.save.assert_called_once()
        mock_create_from_sequence.assert_any_call(100)
        self.assertEqual(mock_create_from_sequence.call_count, 2)

        mock_run_tracker_corp_delay.assert_called_once_with(
            corporation_id=2001,
            killmail_id=123456,
        )
        mock_run_tracker_ally_delay.assert_called_once_with(
            alliance_id=3001,
            killmail_id=123456,
        )
        self.assertEqual(mock_run_tracker_corp_delay.call_count, 1)
        self.assertEqual(mock_run_tracker_ally_delay.call_count, 1)

    @patch(MODULE_PATH + ".Chain")
    @patch(MODULE_PATH + ".store_killmail.si")
    @patch(HELPER_PATH + ".KillmailBody.get")
    @patch(MODULE_PATH + ".CorporationsAudit.objects.get")
    def test_run_tracker_corporation_triggers_store_chain_when_new(
        self,
        mock_corporation_get,
        mock_killmail_get,
        mock_store_killmail_signature,
        mock_chain,
    ):
        corporation = Mock()
        corporation.process_killmail.return_value = True
        mock_corporation_get.return_value = corporation

        killmail = Mock()
        killmail.id = 999
        mock_killmail_get.return_value = killmail

        signature = Mock()
        mock_store_killmail_signature.return_value = signature

        chain_instance = Mock()
        mock_chain.return_value = chain_instance

        run_tracker_corporation(corporation_id=2001, killmail_id=999)

        corporation.process_killmail.assert_called_once_with(killmail)
        mock_store_killmail_signature.assert_called_once_with(999)
        mock_chain.assert_called_once_with(signature)
        chain_instance.delay.assert_called_once()

    @patch(MODULE_PATH + ".Chain")
    @patch(MODULE_PATH + ".store_killmail.si")
    @patch(HELPER_PATH + ".KillmailBody.get")
    @patch(MODULE_PATH + ".AlliancesAudit.objects.get")
    def test_run_tracker_alliance_triggers_store_chain_when_new(
        self,
        mock_alliance_get,
        mock_killmail_get,
        mock_store_killmail_signature,
        mock_chain,
    ):
        alliance = Mock()
        alliance.process_killmail.return_value = True
        mock_alliance_get.return_value = alliance

        killmail = Mock()
        killmail.id = 555
        mock_killmail_get.return_value = killmail

        signature = Mock()
        mock_store_killmail_signature.return_value = signature

        chain_instance = Mock()
        mock_chain.return_value = chain_instance

        run_tracker_alliance(alliance_id=3001, killmail_id=555)

        alliance.process_killmail.assert_called_once_with(killmail)
        mock_store_killmail_signature.assert_called_once_with(555)
        mock_chain.assert_called_once_with(signature)
        chain_instance.delay.assert_called_once()

    @patch(HELPER_TASKS_PATH + ".Killmail.objects.filter")
    @patch(HELPER_TASKS_PATH + ".requests.get")
    def test_check_missing_killmails_corporation(self, mock_get, mock_km_filter):
        now = timezone.now()
        time_current = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        mock_response = Mock()
        mock_response.json.return_value = [
            {"killmail_id": 101, "killmail_time": time_current},
            {"killmail_id": 102, "killmail_time": time_current},
            {"killmail_id": 103, "killmail_time": "2020-01-01T00:00:00Z"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Killmail 101 exists in DB, 102 and 103 are missing
        mock_qs_existing = Mock()
        mock_qs_existing.values_list.return_value = [101]
        mock_km_filter.return_value = mock_qs_existing

        result = check_missing_killmails(corporation_id=2001, pages=1)

        self.assertEqual(len(result), 2)
        missing_ids = [km["killmail_id"] for km in result]
        self.assertEqual(missing_ids, [103, 102])

    @patch(HELPER_TASKS_PATH + ".Killmail.objects.filter")
    @patch(HELPER_TASKS_PATH + ".requests.get")
    def test_check_missing_killmails_alliance(self, mock_get, mock_km_filter):
        mock_response = Mock()
        mock_response.json.return_value = [{"killmail_id": 501}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_qs_existing = Mock()
        mock_qs_existing.values_list.return_value = []
        mock_km_filter.return_value = mock_qs_existing

        result = check_missing_killmails(alliance_id=3001, pages=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["killmail_id"], 501)

    def test_check_missing_killmails_raises_without_id(self):
        with self.assertRaises(ValueError):
            check_missing_killmails()

    @patch(MODULE_PATH + ".Killmail.objects.create_from_killmail")
    @patch(MODULE_PATH + ".KillmailBody.create_from_zkb_dict")
    @patch(MODULE_PATH + ".Killmail.objects.filter")
    def test_import_missing_killmails_from_zkb(
        self, mock_filter, mock_create_body, mock_create_km
    ):
        # 3 items:
        # km 1: already exists -> skipped
        # km 2: valid -> imported
        # km 3: body creation fails -> failed
        mock_exists = Mock()
        mock_exists.exists.side_effect = [True, False, False]
        mock_filter.return_value = mock_exists

        body_2 = Mock()
        mock_create_body.side_effect = [body_2, None]

        raw_killmails = [
            {"killmail_id": 101},
            {"killmail_id": 102},
            {"killmail_id": 103},
        ]

        import_missing_killmails_from_zkb(
            missing_killmails=raw_killmails,
            corporation_id=2001,
        )

        mock_create_km.assert_called_once_with(body_2)
        body_2.save.assert_called_once()

    @patch(MODULE_PATH + ".import_missing_killmails_from_zkb.delay")
    @patch(MODULE_PATH + ".check_missing_killmails")
    def test_check_and_import_corporation_killmails_task(
        self, mock_check, mock_import_delay
    ):
        missing_data = [{"killmail_id": 101}]
        mock_check.return_value = missing_data

        check_and_import_corporation_killmails_task(corporation_id=2001, pages=3)

        mock_check.assert_called_once_with(corporation_id=2001, pages=3)
        mock_import_delay.assert_called_once_with(
            missing_killmails=missing_data, corporation_id=2001
        )

    @patch(MODULE_PATH + ".import_missing_killmails_from_zkb.delay")
    @patch(MODULE_PATH + ".check_missing_killmails")
    def test_check_and_import_corporation_killmails_task_empty(
        self, mock_check, mock_import_delay
    ):
        mock_check.return_value = []

        check_and_import_corporation_killmails_task(corporation_id=2001, pages=3)

        mock_check.assert_called_once_with(corporation_id=2001, pages=3)
        mock_import_delay.assert_not_called()

    @patch(MODULE_PATH + ".import_missing_killmails_from_zkb.delay")
    @patch(MODULE_PATH + ".check_missing_killmails")
    def test_check_and_import_alliance_killmails_task(
        self, mock_check, mock_import_delay
    ):
        missing_data = [{"killmail_id": 501}]
        mock_check.return_value = missing_data

        check_and_import_alliance_killmails_task(alliance_id=3001, pages=2)

        mock_check.assert_called_once_with(alliance_id=3001, pages=2)
        mock_import_delay.assert_called_once_with(
            missing_killmails=missing_data, alliance_id=3001
        )

    @patch(MODULE_PATH + ".update_missing_solar_systems_task.delay")
    @patch(MODULE_PATH + ".check_and_import_alliance_killmails_task.delay")
    @patch(MODULE_PATH + ".check_and_import_corporation_killmails_task.delay")
    @patch(MODULE_PATH + ".AlliancesAudit.objects.select_related")
    @patch(MODULE_PATH + ".CorporationsAudit.objects.select_related")
    def test_run_tracker_missing_data_sequential(
        self,
        mock_corps_select,
        mock_allys_select,
        mock_corp_delay,
        mock_ally_delay,
        mock_solar_delay,
    ):
        corp_audit = Mock()
        corp_audit.corporation.corporation_id = 2001
        corp_audit.last_missing_check = None
        mock_corps_select.return_value.order_by.return_value = [corp_audit]

        ally_audit = Mock()
        ally_audit.alliance.alliance_id = 3001
        ally_audit.last_missing_check = None
        mock_allys_select.return_value.order_by.return_value = [ally_audit]

        run_tracker_missing_data(pages=2, batch_size=50)

        self.assertIsNotNone(corp_audit.last_missing_check)
        corp_audit.save.assert_called_once_with(update_fields=["last_missing_check"])
        mock_corp_delay.assert_called_once_with(corporation_id=2001, pages=2)

        self.assertIsNotNone(ally_audit.last_missing_check)
        ally_audit.save.assert_called_once_with(update_fields=["last_missing_check"])
        mock_ally_delay.assert_called_once_with(alliance_id=3001, pages=2)
        mock_solar_delay.assert_called_once_with(batch_size=50, min_reserve_tokens=600)

    @patch(MODULE_PATH + ".KillmailBody.get_region_id", return_value=10000002)
    @patch(MODULE_PATH + ".Killmail.objects.filter")
    @patch(MODULE_PATH + ".esi")
    @patch(MODULE_PATH + ".get_esi_killmail_bucket_remaining", return_value=800)
    def test_fetch_solar_system_id_for_killmail_success(
        self, mock_get_bucket, mock_esi, mock_km_filter, mock_get_region
    ):
        mock_result = Mock(solar_system_id=30000142)
        mock_esi.client.Killmails.GetKillmailsKillmailIdKillmailHash.return_value.result.return_value = (
            mock_result
        )
        mock_filter_obj = Mock()
        mock_km_filter.return_value = mock_filter_obj

        result = fetch_solar_system_id_for_killmail(
            killmail_id=101, killmail_hash="hash101", min_reserve_tokens=600
        )

        self.assertEqual(result, 30000142)
        mock_esi.client.Killmails.GetKillmailsKillmailIdKillmailHash.assert_called_once_with(
            killmail_hash="hash101",
            killmail_id=101,
        )
        mock_km_filter.assert_called_once_with(killmail_id=101, hash="hash101")
        mock_filter_obj.update.assert_called_once_with(
            victim_solar_system_id=30000142,
            victim_region_id=10000002,
        )

    @patch(MODULE_PATH + ".esi")
    @patch(MODULE_PATH + ".get_esi_killmail_bucket_remaining", return_value=550)
    def test_fetch_solar_system_id_for_killmail_skips_when_rate_limited(
        self, mock_get_bucket, mock_esi
    ):
        result = fetch_solar_system_id_for_killmail(
            killmail_id=101, killmail_hash="hash101", min_reserve_tokens=600
        )

        self.assertIsNone(result)
        mock_esi.client.Killmails.GetKillmailsKillmailIdKillmailHash.assert_not_called()

    @patch(MODULE_PATH + ".esi")
    @patch(MODULE_PATH + ".get_esi_killmail_bucket_remaining", return_value=800)
    def test_fetch_solar_system_id_for_killmail_handles_exception(
        self, mock_get_bucket, mock_esi
    ):
        mock_esi.client.Killmails.GetKillmailsKillmailIdKillmailHash.side_effect = (
            Exception("ESI request error")
        )

        result = fetch_solar_system_id_for_killmail(
            killmail_id=101, killmail_hash="hash101", min_reserve_tokens=600
        )

        self.assertIsNone(result)
