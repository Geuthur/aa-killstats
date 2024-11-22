"""Generate AllianceAuth test objects from JSON data."""

import json
from pathlib import Path

from django.utils import timezone
from eveuniverse.models import EveEntity, EveType

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)

from killstats.models import AlliancesAudit, Attacker, CorporationsAudit, Killmail
from killstats.tests.testdata.load_eveuniverse import load_eveuniverse


def _load_killmail_data():
    with open(Path(__file__).parent / "killmails.json", encoding="utf-8") as fp:
        return json.load(fp)


def _load_get_bulk_data():
    with open(Path(__file__).parent / "get_bulk.json", encoding="utf-8") as fp:
        return json.load(fp)


_killstats_data = _load_killmail_data()


def load_killstats_all():
    load_eveuniverse()
    load_killstats()
    load_corporationaudit()
    load_allianceaudit()


def load_corporationaudit():
    CorporationsAudit.objects.all().delete()
    CorporationsAudit.objects.update_or_create(
        id=1,
        corporation=EveCorporationInfo.objects.get(corporation_id=20000001),
        owner=EveCharacter.objects.get(character_id=1001),
    )
    CorporationsAudit.objects.update_or_create(
        id=2,
        corporation=EveCorporationInfo.objects.get(corporation_id=20000002),
        owner=EveCharacter.objects.get(character_id=1002),
    )


def load_allianceaudit():
    AlliancesAudit.objects.all().delete()
    AlliancesAudit.objects.update_or_create(
        id=1,
        alliance=EveAllianceInfo.objects.get(alliance_id=30000001),
        owner=EveCharacter.objects.get(character_id=1001),
    )
    AlliancesAudit.objects.update_or_create(
        id=2,
        alliance=EveAllianceInfo.objects.get(alliance_id=30000002),
        owner=EveCharacter.objects.get(character_id=1002),
    )


def load_killstats():
    Killmail.objects.all().delete()
    Attacker.objects.all().delete()
    for killmail in _killstats_data.get("Killmail"):
        km, _ = Killmail.objects.update_or_create(
            killmail_id=killmail.get("killmail_id"),
            killmail_date=timezone.datetime.strptime(
                killmail.get("killmail_date"), "%Y-%m-%d %H:%M:%S"
            ),
            victim=EveEntity.objects.get(id=killmail.get("victim")),
            victim_ship=EveType.objects.get(id=killmail.get("victim_ship")),
            victim_corporation_id=killmail.get("victim_corporation_id"),
            victim_alliance_id=killmail.get("victim_alliance_id", None),
            victim_total_value=killmail.get("victim_total_value"),
            victim_fitted_value=killmail.get("victim_fitted_value"),
            victim_destroyed_value=killmail.get("victim_destroyed_value"),
            victim_dropped_value=killmail.get("victim_dropped_value"),
            victim_region_id=killmail.get("victim_region_id"),
            victim_solar_system_id=killmail.get("victim_solar_system_id"),
            victim_position_x=killmail.get("victim_position_x"),
            victim_position_y=killmail.get("victim_position_y"),
            victim_position_z=killmail.get("victim_position_z"),
            hash=killmail.get("hash"),
        )

        attackers = killmail.get("attackers")
        for attacker in attackers:
            character = None
            corporation = None
            alliance = None
            ship = None

            character_id = attacker.get("character_id", None)
            corporation_id = attacker.get("corporation_id", None)
            alliance_id = attacker.get("alliance_id", None)
            ship_type_id = attacker.get("ship_type_id", None)

            if character_id is not None:
                character = EveEntity.objects.get(id=character_id)
            if corporation_id is not None:
                corporation = EveEntity.objects.get(id=corporation_id)
            if alliance_id is not None:
                alliance = EveEntity.objects.get(id=alliance_id)
            if ship_type_id is not None:
                ship = EveType.objects.get(id=ship_type_id)

            Attacker.objects.update_or_create(
                killmail=km,
                character=character,
                corporation=corporation,
                alliance=alliance,
                ship=ship,
                damage_done=attacker.get("damage_done", None),
                final_blow=attacker.get("final_blow", None),
                weapon_type_id=attacker.get("weapon_type_id", None),
                security_status=attacker.get("security_status", None),
            )
