# Standard Library
import importlib
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

# Third Party
from evesde_factory.allianceauth import UserFactory

# AA Killstats
from killstats.models.general import General
from killstats.tests import AuthTestCase


class TestCharlinkHook(AuthTestCase):
    """charlink is an optional package, so the tests load the hook with a stub of it."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        utils = ModuleType("charlink.app_imports.utils")
        utils.AppImport = lambda app, imports: SimpleNamespace(imports=imports)
        utils.LoginImport = lambda **kwargs: SimpleNamespace(**kwargs)
        stubs = {
            "charlink": ModuleType("charlink"),
            "charlink.app_imports": ModuleType("charlink.app_imports"),
            "charlink.app_imports.utils": utils,
        }
        with patch.dict(sys.modules, stubs):
            sys.modules.pop("killstats.thirdparty.charlink_hook", None)
            module = importlib.import_module("killstats.thirdparty.charlink_hook")
        sys.modules.pop("killstats.thirdparty.charlink_hook", None)
        cls.login_import = module.app_import.imports[0]

    def test_check_permissions_allows_user_with_basic_access(self):
        self.assertTrue(self.login_import.check_permissions(self.user))

    def test_check_permissions_denies_user_without_basic_access(self):
        self.assertFalse(self.login_import.check_permissions(UserFactory()))

    def test_check_permissions_uses_general_manager(self):
        with patch.object(
            General.objects, "has_basic_access", return_value=True
        ) as mock_access:
            self.assertTrue(self.login_import.check_permissions(self.user))
        mock_access.assert_called_once_with(self.user)
