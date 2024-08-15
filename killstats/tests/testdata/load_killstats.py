"""Generate AllianceAuth test objects from JSON data."""

import json
from datetime import datetime
from pathlib import Path

from eveuniverse.models import EveType

from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)

from killstats.models import AlliancesAudit, CorporationsAudit, EveEntity, Killmail
from killstats.tests.testdata.load_eveuniverse import load_eveuniverse


def _load_eveentity_data():
    with open(Path(__file__).parent / "eveentity.json", encoding="utf-8") as fp:
        return json.load(fp)


_entities_data = _load_eveentity_data()


def _load_killmail_data():
    with open(Path(__file__).parent / "killmails.json", encoding="utf-8") as fp:
        return json.load(fp)


def _load_get_bulk_data():
    with open(Path(__file__).parent / "get_bulk.json", encoding="utf-8") as fp:
        return json.load(fp)


_killstats_data = _load_killmail_data()


def load_killstats_all():
    load_eveentity()
    load_eveuniverse()
    load_killstats()
    load_corporationaudit()
    load_allianceaudit()


def load_eveentity():
    EveEntity.objects.all().delete()
    for character_info in _entities_data.get("EveEntity"):
        EveEntity.objects.create(
            eve_id=character_info.get("eve_id"),
            name=character_info.get("name"),
            category=character_info.get("category"),
        )


def load_corporationaudit():
    CorporationsAudit.objects.all().delete()
    CorporationsAudit.objects.update_or_create(
        id=1,
        corporation=EveCorporationInfo.objects.get(corporation_id=2001),
        owner=EveCharacter.objects.get(character_id=1001),
    )
    CorporationsAudit.objects.update_or_create(
        id=2,
        corporation=EveCorporationInfo.objects.get(corporation_id=2002),
        owner=EveCharacter.objects.get(character_id=1002),
    )


def load_allianceaudit():
    AlliancesAudit.objects.all().delete()
    AlliancesAudit.objects.update_or_create(
        id=1,
        alliance=EveAllianceInfo.objects.get(alliance_id=3001),
        owner=EveCharacter.objects.get(character_id=1001),
    )
    AlliancesAudit.objects.update_or_create(
        id=2,
        alliance=EveAllianceInfo.objects.get(alliance_id=3002),
        owner=EveCharacter.objects.get(character_id=1002),
    )


def load_killstats():
    Killmail.objects.all().delete()
    for killmail in _killstats_data.get("Killmail"):
        Killmail.objects.update_or_create(
            killmail_id=killmail.get("killmail_id"),
            killmail_date=datetime.strptime(
                killmail.get("killmail_date"), "%Y-%m-%d %H:%M:%S"
            ),
            victim=EveEntity.objects.get(eve_id=killmail.get("victim")),
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
            attackers=killmail.get("attackers"),
        )
