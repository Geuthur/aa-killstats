"""Unit tests for killstats API helper functions."""

# EVE SDE & Alliance Auth Factories
# Third Party
from evesde_factory.allianceauth import (
    EveAllianceInfoFactory,
    EveCharacterFactory,
    EveCorporationInfoFactory,
)
from evesde_factory.utils import add_character_to_user

# AA Killstats
from killstats.api.helpers import get_alliances, get_corporations, get_permission
from killstats.tests import AuthTestCase
from killstats.tests.testdata.killstats import (
    AlliancesAuditFactory,
    CorporationsAuditFactory,
    UserMainFactory,
)

MODULE_PATH = "killstats.api.helpers"


class TestApiHelpersCorporations(AuthTestCase):
    def test_get_corporations_should_return_corporation_ids_when_audited(self):
        # Test Data
        corp = EveCorporationInfoFactory()
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)
        CorporationsAuditFactory(corporation=corp, owner=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        corporations = get_corporations(request)

        # Expected Result
        self.assertEqual(corporations, [corp.corporation_id])

    def test_get_corporations_should_return_empty_when_no_audit_exists(self):
        # Test Data
        corp = EveCorporationInfoFactory()
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        corporations = get_corporations(request)

        # Expected Result
        self.assertEqual(corporations, [])

    def test_get_corporations_should_return_all_linked_corporations_when_main_is_audited(
        self,
    ):
        # Test Data
        corp1 = EveCorporationInfoFactory()
        corp2 = EveCorporationInfoFactory()
        char1 = EveCharacterFactory(corporation=corp1)
        char2 = EveCharacterFactory(corporation=corp2)
        user = UserMainFactory(main_character__character=char1)
        add_character_to_user(user=user, character=char2)
        CorporationsAuditFactory(corporation=corp1, owner=char1)
        CorporationsAuditFactory(corporation=corp2, owner=char2)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        corporations = get_corporations(request)

        # Expected Result
        self.assertCountEqual(
            corporations, [corp1.corporation_id, corp2.corporation_id]
        )


class TestApiHelpersAlliances(AuthTestCase):
    def test_get_alliances_should_return_alliance_ids_when_audited(self):
        # Test Data
        alliance = EveAllianceInfoFactory()
        corp = EveCorporationInfoFactory(alliance=alliance)
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)
        AlliancesAuditFactory(alliance=alliance, owner=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        alliances = get_alliances(request)

        # Expected Result
        self.assertEqual(alliances, [alliance.alliance_id])

    def test_get_alliances_should_return_empty_when_no_audit_exists(self):
        # Test Data
        alliance = EveAllianceInfoFactory()
        corp = EveCorporationInfoFactory(alliance=alliance)
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        alliances = get_alliances(request)

        # Expected Result
        self.assertEqual(alliances, [])

    def test_get_alliances_should_return_empty_when_character_has_no_alliance(self):
        # Test Data
        corp = EveCorporationInfoFactory(create_alliance=False)
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        alliances = get_alliances(request)

        # Expected Result
        self.assertEqual(alliances, [])

    def test_get_alliances_should_return_all_linked_alliances_when_main_is_audited(
        self,
    ):
        # Test Data
        alliance1 = EveAllianceInfoFactory()
        alliance2 = EveAllianceInfoFactory()
        corp1 = EveCorporationInfoFactory(alliance=alliance1)
        corp2 = EveCorporationInfoFactory(alliance=alliance2)
        char1 = EveCharacterFactory(corporation=corp1)
        char2 = EveCharacterFactory(corporation=corp2)
        user = UserMainFactory(main_character__character=char1)
        add_character_to_user(user=user, character=char2)
        AlliancesAuditFactory(alliance=alliance1, owner=char1)
        AlliancesAuditFactory(alliance=alliance2, owner=char2)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        alliances = get_alliances(request)

        # Expected Result
        self.assertCountEqual(alliances, [alliance1.alliance_id, alliance2.alliance_id])


class TestApiHelpersPermissions(AuthTestCase):
    def test_get_permission_corporation_should_return_true_and_corporations_when_data_exists(
        self,
    ):
        # Test Data
        corp = EveCorporationInfoFactory()
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)
        CorporationsAuditFactory(corporation=corp, owner=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        has_permission, result = get_permission(request, entity_type="corporation")

        # Expected Result
        self.assertTrue(has_permission)
        self.assertEqual(result, [corp.corporation_id])

    def test_get_permission_corporation_should_return_false_when_no_data_exists(self):
        # Test Data
        corp = EveCorporationInfoFactory()
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        has_permission, result = get_permission(request, entity_type="corporation")

        # Expected Result
        self.assertFalse(has_permission)
        self.assertEqual(result, [{"No Data": "No data available for the entity"}])

    def test_get_permission_alliance_should_return_true_and_alliances_when_data_exists(
        self,
    ):
        # Test Data
        alliance = EveAllianceInfoFactory()
        corp = EveCorporationInfoFactory(alliance=alliance)
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)
        AlliancesAuditFactory(alliance=alliance, owner=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        has_permission, result = get_permission(request, entity_type="alliance")

        # Expected Result
        self.assertTrue(has_permission)
        self.assertEqual(result, [alliance.alliance_id])

    def test_get_permission_alliance_should_return_false_when_no_data_exists(self):
        # Test Data
        alliance = EveAllianceInfoFactory()
        corp = EveCorporationInfoFactory(alliance=alliance)
        char = EveCharacterFactory(corporation=corp)
        user = UserMainFactory(main_character__character=char)

        request = self.factory.get("/")
        request.user = user

        # Test Action
        has_permission, result = get_permission(request, entity_type="alliance")

        # Expected Result
        self.assertFalse(has_permission)
        self.assertEqual(result, [{"No Data": "No data available for the entity"}])
