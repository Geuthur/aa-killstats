# Third Party
from charlink.app_imports.utils import AppImport, LoginImport

# Django
from django.contrib.auth.models import Permission
from django.db.models import Exists, OuterRef

# Alliance Auth
from allianceauth.authentication.models import User
from allianceauth.eveonline.models import EveCharacter

# AA Killstats
from killstats import __app_name__
from killstats.app_settings import KILLSTATS_APP_NAME
from killstats.models.killstatsaudit import CorporationsAudit


# pylint: disable=unused-argument, duplicate-code
def _add_corporationaudit(request, token):
    corporation = CorporationsAudit.objects.update_or_create(
        owner=EveCharacter.objects.get_character_by_id(token.character_id),
        corporation=EveCharacter.objects.get_character_by_id(
            token.character_id
        ).corporation,
    )[0]
    assert corporation.pk


def _is_character_added_corpaudit(character: EveCharacter):
    return CorporationsAudit.objects.filter(owner=character).exists()


def _users_with_perms_corpaudit():
    permission = Permission.objects.get(
        content_type__app_label=__app_name__, codename="basic_access"
    )
    users_qs = (
        permission.user_set.all()
        | User.objects.filter(
            groups__in=list(permission.group_set.values_list("pk", flat=True))
        )
        | User.objects.select_related("profile").filter(
            profile__state__in=list(permission.state_set.values_list("pk", flat=True))
        )
        | User.objects.filter(is_superuser=True)
    )
    return users_qs.distinct()


app_import = AppImport(
    "killstats",
    [
        LoginImport(
            app_label="killstats",
            unique_id="default",
            field_label="Corporation" + " " + KILLSTATS_APP_NAME,
            add_character=_add_corporationaudit,
            scopes=[],
            check_permissions=lambda user: user.has_perm("killstats.basic_access"),
            is_character_added=_is_character_added_corpaudit,
            is_character_added_annotation=Exists(
                CorporationsAudit.objects.filter(
                    owner__character_id=OuterRef("character_id")
                )
            ),
            get_users_with_perms=_users_with_perms_corpaudit,
            default_initial_selection=False,
        ),
    ],
)
