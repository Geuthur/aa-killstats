from unittest.mock import patch

from ninja import NinjaAPI

from django.test import TestCase

from allianceauth.eveonline.models import EveCorporationInfo
from app_utils.testing import create_user_from_evecharacter

from killstats.api.killboard import KillboardCorporationApiEndpoints
from killstats.tests.test_api import _killstasts_api
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all


class ManageApiCorporationEndpointsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()

        cls.user, _ = create_user_from_evecharacter(
            1001,
            permissions=["killstats.basic_access", "killstats.admin_access"],
        )

        cls.user2, _ = create_user_from_evecharacter(
            1002,
            permissions=[
                "killstats.basic_access",
            ],
        )

    def test_killboard_proccess_kills(self):
        pass
