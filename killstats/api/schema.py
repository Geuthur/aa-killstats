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


class KillboardIndex(Schema):
    kills: Optional[list] = None
    losses: Optional[list] = None
    totalKills: Optional[int] = None
    totalLoss: Optional[int] = None
    shame: Optional[list] = None
    fame: Optional[list] = None
    stats: Optional[list] = None
