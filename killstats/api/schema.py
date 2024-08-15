from datetime import datetime
from typing import Optional

from ninja import Schema


class Killboard(Schema):
    kills: Optional[int] = None
    date: Optional[datetime] = None
    character_id: Optional[int] = None
    character_name: Optional[str] = None
    ship_id: Optional[int] = None
    ship_name: Optional[str] = None
    hash: Optional[str] = None
    totalValue: Optional[int] = None
    attackers: Optional[list] = None


class KillboardHall(Schema):
    shame: Optional[list] = None
    fame: Optional[list] = None


class KillboardStats(Schema):
    stats: Optional[list] = None


class CorporationAdmin(Schema):
    corporation: Optional[dict] = None


class AllianceAdmin(Schema):
    alliance: Optional[dict] = None
