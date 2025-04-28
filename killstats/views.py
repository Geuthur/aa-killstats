"""App Views"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.functions import ExtractYear
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from esi.decorators import token_required

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)
from allianceauth.eveonline.providers import ObjectNotFound, provider

# AA Killstats
from killstats import __title__
from killstats.models.killboard import Killmail
from killstats.models.killstatsaudit import AlliancesAudit, CorporationsAudit
from killstats.tasks import killmail_update_ally, killmail_update_corp

from .hooks import get_extension_logger

logger = get_extension_logger(__name__)


@login_required
@permission_required("killstats.basic_access")
def killboard_index(request):
    return redirect(
        "killstats:corporation", request.user.profile.main_character.corporation_id
    )


@login_required
@permission_required("killstats.basic_access")
def corporation_view(request, corporation_id=None):
    if corporation_id is None:
        corporation_id = request.user.profile.main_character.corporation_id

    years = (
        Killmail.objects.filter(victim_corporation_id=corporation_id)
        .annotate(year=ExtractYear("killmail_date"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )[:5]

    context = {
        "title": "Corporation Killboard",
        "years": years,
        "entity_pk": corporation_id,
        "entity_type": "corporation",
    }
    return render(request, "killstats/killboard.html", context=context)


@login_required
@permission_required("killstats.basic_access")
def alliance_view(request, alliance_id=None):
    if alliance_id is None:
        try:
            alliance_id = request.user.profile.main_character.alliance_id
            if alliance_id is None:
                raise AttributeError
        except AttributeError:
            messages.error(request, "You do not have an alliance.")
            return redirect("killstats:index")

    years = (
        Killmail.objects.filter(victim_alliance_id=alliance_id)
        .annotate(year=ExtractYear("killmail_date"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )[:5]

    context = {
        "title": "Alliance Killboard",
        "years": years,
        "entity_pk": alliance_id,
        "entity_type": "alliance",
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
    char = get_object_or_404(EveCharacter, character_id=token.character_id)

    try:
        alliance = EveAllianceInfo.objects.get(alliance_id=char.alliance_id)
    except EveAllianceInfo.DoesNotExist:
        try:
            ally_data = provider.get_alliance(char.alliance_id)
            alliance, __ = EveAllianceInfo.objects.get_or_create(
                alliance_id=ally_data.id,
                defaults={
                    "alliance_name": ally_data.name,
                    "alliance_ticker": ally_data.ticker,
                    "executor_corp_id": ally_data.executor_corp_id,
                },
            )
        except ObjectNotFound:
            msg = _("Failed to fetch Alliance data for {alliance_name}").format(
                alliance_name=char.alliance_name,
            )
            messages.warning(request, msg)
            return redirect("killstats:index")

    __, created = AlliancesAudit.objects.update_or_create(alliance=alliance, owner=char)

    if created:
        killmail_update_ally.apply_async(args=[char.alliance_id], priority=6)

    msg = f"{char.alliance_name} successfully added/updated to Killboard"
    messages.info(request, msg)
    return redirect("killstats:index")


@login_required
@permission_required("killstats.basic_access")
def corporation_admin(request):
    """
    Corporation Admin
    """
    context = {
        "title": "Corporation Overview",
    }
    return render(request, "killstats/admin/corporation_admin.html", context=context)


@login_required
@permission_required("killstats.basic_access")
def alliance_admin(request):
    """
    Alliance Admin
    """
    context = {
        "title": "Alliance Overview",
    }
    return render(request, "killstats/admin/alliance_admin.html", context=context)
