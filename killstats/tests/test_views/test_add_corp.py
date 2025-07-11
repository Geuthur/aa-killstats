# Standard Library
from unittest.mock import Mock, patch

# Django
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import (
    EveCorporationInfo,
)
from esi.models import Token

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter

# AA Killstats
from killstats.models.killstatsaudit import CorporationsAudit
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.views import (
    add_corp,
)

MODULE_PATH = "killstats.views"


@patch(MODULE_PATH + ".messages")
class KillstatsAuditTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()

        cls.factory = RequestFactory()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "killstats.basic_access",
                "killstats.admin_access",
            ],
        )

    def _add_corporation(self, user, token):
        request = self.factory.get(reverse("killstats:add_corp"))
        request.user = user
        request.token = token
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        orig_view = add_corp.__wrapped__.__wrapped__.__wrapped__
        return orig_view(request, token)
