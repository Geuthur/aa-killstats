import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from killstats.managers.killmail_core import KillmailManager
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tasks import (
    store_killmail,
)
from killstats.tests.testdata.generate_killstats import (
    create_allianceaudit_from_character_id,
    create_corporationaudit_from_character_id,
)
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_eveuniverse import load_eveuniverse

MODULE_PATH = "killstats.tasks"


def load_test_data(filename):
    with open(filename) as file:
        return json.load(file)


# @patch(MODULE_PATH + ".killmail_update_corp.apply_async", spec=True)
# @patch(MODULE_PATH + ".killmail_update_ally.apply_async", spec=True)
@override_settings(
    CELERY_ALWAYS_EAGER=True,
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    APP_UTILS_OBJECT_CACHE_DISABLED=True,
)
class TestUpdateTasks(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()

        cls.audit = create_corporationaudit_from_character_id(1001)
        cls.audit2 = create_allianceaudit_from_character_id(1001)
