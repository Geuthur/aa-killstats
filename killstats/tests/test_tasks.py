import json
from unittest.mock import MagicMock, call, patch

from django.db import IntegrityError
from django.test import TestCase

from killstats.managers.killmail_core import KillmailManager
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tasks import (
    killmail_fetch_all,
    killmail_update_ally,
    killmail_update_corp,
    store_killmail,
)
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import (
    _load_get_bulk_data,
    load_killstats_all,
)

MODULE_PATH = "killstats.tasks"


def load_test_data(filename):
    with open(filename) as file:
        return json.load(file)


class TestTasks(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()

    @patch(MODULE_PATH + ".killmail_update_corp.apply_async")
    @patch(MODULE_PATH + ".killmail_update_ally.apply_async")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_fetch_all(self, mock_logger, mock_update_ally, mock_update_corp):
        # given
        corp_count = CorporationsAudit.objects.count()
        ally_count = AlliancesAudit.objects.count()
        expected_count = corp_count + ally_count
        # when
        killmail_fetch_all()
        # then
        self.assertEqual(mock_update_corp.call_count, corp_count)
        self.assertEqual(mock_update_ally.call_count, ally_count)
        mock_logger.info.assert_called_once_with(
            "Queued %s Killstats Audit Updates", expected_count
        )

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_update_corp(self, mock_logger, mock_get_killmail_data_bulk):
        # given
        corp = CorporationsAudit.objects.get(corporation__corporation_id=20000001)

        mock_get_killmail_data_bulk.return_value = _load_get_bulk_data()
        # when
        killmail_update_corp(corp.corporation.corporation_id)
        # then
        mock_logger.info.assert_called_once_with(
            "Killboard runs completed. %s killmails received from zKB for %s",
            3,
            corp.corporation.corporation_name,
        )

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_update_ally(self, mock_logger, mock_get_killmail_data_bulk):
        # given
        ally = AlliancesAudit.objects.get(alliance__alliance_id=30000001)

        mock_get_killmail_data_bulk.return_value = _load_get_bulk_data()
        # when
        killmail_update_ally(ally.alliance.alliance_id)
        # then
        mock_logger.info.assert_called_once_with(
            "Killboard runs completed. %s killmails received from zKB for %s",
            3,
            ally.alliance.alliance_name,
        )

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_update_corp_no_new(
        self, mock_logger, mock_get_killmail_data_bulk
    ):
        # given
        corp = CorporationsAudit.objects.get(corporation__corporation_id=20000001)

        mock_get_killmail_data_bulk.return_value = None
        # when
        killmail_update_corp(corp.corporation.corporation_id)
        # then
        mock_logger.debug.assert_called_once_with("No new Killmail found.")

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_update_ally_no_new(
        self, mock_logger, mock_get_killmail_data_bulk
    ):
        # given
        ally = AlliancesAudit.objects.get(alliance__alliance_id=30000001)

        mock_get_killmail_data_bulk.return_value = None
        # when
        killmail_update_ally(ally.alliance.alliance_id)
        # then
        mock_logger.debug.assert_called_once_with("No new Killmail found.")

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_store(self, mock_logger, mock_get_killmail_data_bulk):
        # given
        killmail_list = _load_get_bulk_data()
        for killmail_dict in killmail_list:
            killmail = KillmailManager._create_from_dict(killmail_dict)
            killmail.save()
        # when
        store_killmail(killmail.id)
        # then
        mock_logger.debug.assert_called_once_with("%s: Stored killmail", 119271433)

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".Killmail.objects.create_from_killmail")
    @patch(MODULE_PATH + ".KillmailManager.get")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_store_and_already_exist(
        self,
        mock_logger,
        mock_get,
        mock_create_from_killmail,
        mock_get_killmail_data_bulk,
    ):
        # given
        killmail_id = 119271433
        killmail_mock = MagicMock(id=killmail_id)
        mock_get.return_value = killmail_mock
        mock_create_from_killmail.side_effect = IntegrityError
        # when
        store_killmail(killmail_id)
        # then
        mock_logger.warning.assert_called_once_with(
            "%s: Failed to store killmail, because it already exists", killmail_id
        )

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".Killmail.objects.all")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_update_corp_existing_kms(
        self, mock_logger, mock_existing, mock_get_killmail_data_bulk
    ):
        # given
        corp = CorporationsAudit.objects.get(corporation__corporation_id=20000001)
        existing_kms = [119324952, 119324561, 119271433]
        mock_get_killmail_data_bulk.return_value = _load_get_bulk_data()
        mock_existing.return_value.values_list.return_value = existing_kms
        # when
        killmail_update_corp(corp.corporation.corporation_id)
        # then
        mock_logger.debug.assert_called_with("No new Killmail found.")

    @patch(MODULE_PATH + ".KillmailManager.get_killmail_data_bulk")
    @patch(MODULE_PATH + ".Killmail.objects.all")
    @patch(MODULE_PATH + ".logger")
    def test_killmail_update_ally_existing_kms(
        self, mock_logger, mock_existing, mock_get_killmail_data_bulk
    ):
        # given
        ally = AlliancesAudit.objects.get(alliance__alliance_id=30000001)
        existing_kms = [119324952, 119324561, 119271433]
        mock_get_killmail_data_bulk.return_value = _load_get_bulk_data()
        mock_existing.return_value.values_list.return_value = existing_kms
        # when
        killmail_update_ally(ally.alliance.alliance_id)
        # then
        mock_logger.debug.assert_called_with("No new Killmail found.")
