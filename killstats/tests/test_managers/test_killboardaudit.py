from django.test import TestCase

from allianceauth.eveonline.models import EveCharacter
from app_utils.testing import create_user_from_evecharacter

from killstats.models.killstatsaudit import KillstatsAudit
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_killstats import load_killstats_all


class KillstatsAuditQuerySetTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_killstats_all()

    def test_visible_to_superuser(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        self.user.is_superuser = True
        self.user.save()
        # when
        result = KillstatsAudit.objects.visible_to(self.user)
        expected_result = KillstatsAudit.objects.all()
        # then
        self.assertEqual(list(result), list(expected_result))

    def test_visible_to_admin_access(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "killstats.admin_access",
            ],
        )
        # when
        expected_result = KillstatsAudit.objects.all()
        result = KillstatsAudit.objects.visible_to(self.user)
        # then
        self.assertEqual(list(result), list(expected_result))

    def test_visible_to_no_access(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        # when
        expected_result = []
        result = KillstatsAudit.objects.visible_to(self.user)
        # then
        self.assertEqual(list(result), list(expected_result))
