import json
from unittest.mock import MagicMock, call, patch

from django.db import IntegrityError
from django.test import TestCase

from killstats.managers.killmail_core import KillmailManager
from killstats.models.killstatsaudit import KillstatsAudit
from killstats.tasks import killmail_fetch_all, killmail_update_corp, store_killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import (
    _load_get_bulk_data,
    load_killstats_all,
)

MODULE_PATH = "killstats.models.killstatsaudit"


class TestKillstatsAuditModel(TestCase):
    @classmethod
    def setUp(self):
        load_allianceauth()
        load_killstats_all()

    def test_str(self):
        self.audit = KillstatsAudit.objects.get(corporation__corporation_id=2001)
        self.assertEqual(str(self.audit), "Hell RiderZ's Killstats Data")
