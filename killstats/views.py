"""App Views"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

# Django
from django.shortcuts import redirect, render
from esi.decorators import token_required

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)

# AA Killstats
from killstats import __title__
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tasks import killmail_update_ally, killmail_update_corp

from .hooks import get_extension_logger

logger = get_extension_logger(__name__)


@login_required
@permission_required("killstats.basic_access")
def killboard_index(request, corporation_pk=0, alliance_pk=0):
    context = {
        "corporation_pk": corporation_pk,
        "alliance_pk": alliance_pk,
    }
    return render(request, "killstats/killboard.html", context=context)


@login_required
@token_required(scopes=("publicData"))
@permission_required(["killstats.admin_access"])
def add_corp(request, token):
    char = EveCharacter.objects.get_character_by_id(token.character_id)
    if char:
        # Check if it is a NPC Corporation
        if char.corporation_id < 10_000_000:
            msg = "Cannot add NPC Corporation to Killboard"
            messages.error(request, msg)
            return redirect("killstats:index")

        corp, _ = EveCorporationInfo.objects.get_or_create(
            corporation_id=char.corporation_id,
            defaults={
                "member_count": 0,
                "corporation_ticker": char.corporation_ticker,
                "corporation_name": char.corporation_name,
            },
        )

        _, created = CorporationsAudit.objects.update_or_create(
            corporation=corp, owner=char
        )
        if created:
            killmail_update_corp.apply_async(args=[char.corporation_id], priority=6)
        msg = f"{char.corporation_name} successfully added/updated to Killboard"
        messages.info(request, msg)
        return redirect("killstats:index")

    msg = "Failed to add Corporation to Killboard"
    messages.error(request, msg)
    return redirect("killstats:index")


@login_required
@token_required(scopes=("publicData"))
@permission_required(["killstats.admin_access"])
def add_alliance(request, token):
    char = EveCharacter.objects.get_character_by_id(token.character_id)
    if char:
        if char.alliance_id is None:
            msg = "Character is not in an Alliance"
            messages.error(request, msg)
            return redirect("killstats:index")
        try:
            alliance = EveAllianceInfo.objects.get(alliance_id=char.alliance_id)
        except EveAllianceInfo.DoesNotExist:
            alliance = EveAllianceInfo.objects.create_alliance(
                alliance_id=char.alliance_id
            )

        if alliance:
            _, created = AlliancesAudit.objects.update_or_create(
                alliance=alliance, owner=char
            )
            if created:
                killmail_update_ally.apply_async(args=[char.alliance_id], priority=6)
            msg = f"{char.alliance_name} successfully added/updated to Killboard"
            messages.info(request, msg)
            return redirect("killstats:index")

    msg = "Failed to add Alliance to Killboard"
    messages.error(request, msg)
    return redirect("killstats:index")


@login_required
@permission_required("killstats.basic_access")
def corporation_admin(request):
    """
    Corporation Admin
    """
    context = {}
    return render(request, "killstats/admin/corporation_admin.html", context=context)


@login_required
@permission_required("killstats.basic_access")
def alliance_admin(request):
    """
    Alliance Admin
    """
    context = {}
    return render(request, "killstats/admin/alliance_admin.html", context=context)
