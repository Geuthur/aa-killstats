"""App Views"""

from django.contrib import messages

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from esi.decorators import token_required

from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# AA Killstats
from killstats import __title__
from killstats.models.killstatsaudit import KillstatsAudit
from killstats.tasks import killmail_update_corp

from .hooks import get_extension_logger

logger = get_extension_logger(__name__)


@login_required
@permission_required("killstats.basic_access")
def killboard_index(request):
    return render(request, "killstats/killboard.html")


@login_required
@token_required(scopes=("publicData"))
@permission_required(["killstats.admin_access"])
def add_corp(request, token):
    char = EveCharacter.objects.get_character_by_id(token.character_id)
    if char:
        corp, _ = EveCorporationInfo.objects.get_or_create(
            corporation_id=char.corporation_id,
            defaults={
                "member_count": 0,
                "corporation_ticker": char.corporation_ticker,
                "corporation_name": char.corporation_name,
            },
        )

        _, created = KillstatsAudit.objects.update_or_create(
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
