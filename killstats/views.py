"""App Views"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required

# AA Killstats
from killstats import __title__, __version__
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


@login_required
@permission_required("killstats.basic_access")
def react_base(request):
    """React Frontend SPA Base View."""
    context = {
        "app_name": "killstats",
        "title": "Killstats",
        "version": __version__,
    }
    return render(request, "killstats/react_killboard.html", context=context)


@login_required
@permission_required("killstats.basic_access")
def killboard_index(request):
    main_char = getattr(getattr(request.user, "profile", None), "main_character", None)
    corp_id = getattr(main_char, "corporation_id", None)
    if corp_id:
        return redirect("killstats:corporation", corporation_id=corp_id)
    return redirect("killstats:react_base")


@login_required
@permission_required("killstats.basic_access")
def corporation_view(request, corporation_id=None):
    """Corporation Killboard View (React Frontend)."""
    if corporation_id is None:
        main_char = getattr(
            getattr(request.user, "profile", None), "main_character", None
        )
        corporation_id = getattr(main_char, "corporation_id", 0)

    context = {
        "app_name": "killstats",
        "title": "Corporation Killstats",
        "entity_pk": corporation_id or 0,
        "entity_type": "corporation",
        "version": __version__,
    }
    return render(request, "killstats/react_killboard.html", context=context)


@login_required
@permission_required("killstats.basic_access")
def alliance_view(request, alliance_id=None):
    """Alliance Killboard View (React Frontend)."""
    if alliance_id is None:
        main_char = getattr(
            getattr(request.user, "profile", None), "main_character", None
        )
        alliance_id = getattr(main_char, "alliance_id", None)
        if alliance_id is None:
            messages.error(request, _("You do not have an alliance."))
            return redirect("killstats:index")

    context = {
        "app_name": "killstats",
        "title": "Alliance Killstats",
        "entity_pk": alliance_id,
        "entity_type": "alliance",
        "version": __version__,
    }
    return render(request, "killstats/react_killboard.html", context=context)


@login_required
@permission_required("killstats.basic_access")
def corporation_admin(request):
    """Corporation Overview (React Frontend)."""
    context = {
        "app_name": "killstats",
        "title": "Corporation Overview",
        "version": __version__,
    }
    return render(request, "killstats/react_killboard.html", context=context)


@login_required
@permission_required("killstats.basic_access")
def alliance_admin(request):
    """Alliance Overview (React Frontend)."""
    context = {
        "app_name": "killstats",
        "title": "Alliance Overview",
        "version": __version__,
    }
    return render(request, "killstats/react_killboard.html", context=context)


@login_required
@token_required(scopes=("publicData"))
@permission_required(["killstats.admin_access"])
def add_corp(request, token):
    char = get_object_or_404(EveCharacter, character_id=token.character_id)

    # Check if it is a NPC Corporation
    if not char.corporation_id or char.corporation_id < 10_000_000:
        msg = _("Cannot add NPC Corporation to Killstats")
        messages.error(request, msg)
        return redirect("killstats:index")

    corp = EveCorporationInfo.objects.get_or_create(
        corporation_id=char.corporation_id,
        defaults={
            "member_count": 0,
            "corporation_ticker": char.corporation_ticker,
            "corporation_name": char.corporation_name,
        },
    )[0]

    audit = CorporationsAudit.objects.update_or_create(corporation=corp, owner=char)[0]

    msg = (
        f"{audit.corporation.corporation_name} successfully added/updated to Killstats"
    )
    messages.info(request, msg)
    return redirect("killstats:corporation", corporation_id=corp.corporation_id)


@login_required
@token_required(scopes=("publicData"))
@permission_required(["killstats.admin_access"])
def add_alliance(request, token):
    char = get_object_or_404(EveCharacter, character_id=token.character_id)

    # Check if character belongs to an NPC Corporation
    if not char.corporation_id or char.corporation_id < 10_000_000:
        msg = _("Cannot add Alliance for a character belonging to an NPC Corporation")
        messages.error(request, msg)
        return redirect("killstats:index")

    # Check if character belongs to a valid player Alliance
    if not char.alliance_id or char.alliance_id < 10_000_000:
        msg = _("Character does not belong to a valid player Alliance")
        messages.error(request, msg)
        return redirect("killstats:index")

    try:
        alliance = EveAllianceInfo.objects.get(
            alliance_id=char.alliance_id,
        )
        audit = AlliancesAudit.objects.update_or_create(alliance=alliance, owner=char)[
            0
        ]
        msg = _("{alliance_name} successfully added/updated to Killstats").format(
            alliance_name=audit.alliance.alliance_name,
        )
    except ObjectDoesNotExist as exc:  # pylint: disable=broad-exception-caught
        msg = _("Alliance {alliance_name} could not be found in Alliance Auth").format(
            alliance_name=char.alliance_name,
        )
        messages.warning(request, msg)
        logger.error(
            "Error fetching alliance data for alliance_id %s: %s",
            char.alliance_id,
            exc,
        )
        return redirect("killstats:index")

    messages.info(request, msg)
    return redirect("killstats:alliance", alliance_id=alliance.alliance_id)


# Backwards compatibility aliases
react_corporation_view = corporation_view
react_alliance_view = alliance_view
