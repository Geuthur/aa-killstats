# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCorporationInfo

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter
from eveuniverse.models import EveEntity, EveType

# AA Killstats
from killstats.models.killstatsaudit import CorporationsAudit
from killstats.tests.testdata.generate_killmail import create_killmail
from killstats.tests.testdata.load_allianceauth import load_allianceauth
from killstats.tests.testdata.load_eveuniverse import load_eveuniverse


class KillstatsAuditMangerTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()

        cls.killmail = create_killmail(
            killmail_id=1,
            killmail_date="2025-10-01T00:00:00Z",
            victim_corporation_id=2001,
            victim_alliance_id=3001,
            victim_region_id=1001,
            victim_solar_system_id=2001,
            victim_position_x=1.0,
            victim_position_y=1.0,
            victim_position_z=1.0,
            victim=EveEntity.objects.get(id=1001),
            victim_ship=EveType.objects.get(id=670),
            victim_total_value=1000,
            victim_fitted_value=500,
            victim_destroyed_value=500,
            victim_dropped_value=500,
        )

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
