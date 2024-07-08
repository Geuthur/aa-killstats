from datetime import timedelta
from unittest.mock import MagicMock, call, patch

from django.test import TestCase
from django.utils import timezone
from esi.errors import TokenExpiredError

from app_utils.testing import create_user_from_evecharacter

from killstats.models.killboard import Killmail
from killstats.tasks import killmail_update_corp
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all

MODULE_PATH = "killstats.tasks"
