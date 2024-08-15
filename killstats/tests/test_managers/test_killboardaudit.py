from django.test import TestCase

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from app_utils.testing import create_user_from_evecharacter

from killstats.models.killstatsaudit import CorporationsAudit
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
        result = CorporationsAudit.objects.visible_to(self.user)
        expected_result = CorporationsAudit.objects.all()
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
        expected_result = CorporationsAudit.objects.all()
        result = CorporationsAudit.objects.visible_to(self.user)
        # then
        self.assertEqual(list(result), list(expected_result))

    def test_visible_to(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        # when
        expected_result = CorporationsAudit.objects.filter(
            corporation=EveCorporationInfo.objects.get(corporation_id=2001)
        )
        result = CorporationsAudit.objects.visible_to(self.user)
        # then
        self.assertEqual(list(result), list(expected_result))

    def test_visible_to_error(self):
        # given
        self.user, self.character_ownership = create_user_from_evecharacter(
            1001,
        )
        self.user.profile.main_character = None
        # when
        result = list(
            CorporationsAudit.objects.visible_to(self.user).values_list(
                "corporation_id", flat=True
            )
        )
        # then
        self.assertEqual(result, [])
