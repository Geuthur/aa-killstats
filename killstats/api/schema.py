# Third Party
from ninja import Schema


class UserData(Schema):
    """
    Schema for user data, including character ID and character name.
    """

    user_id: int
    character_id: int
    character_name: str
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None
    alliance_name: str | None = None
    portrait: str | None = None
    is_admin: bool = False


class CorporationAdmin(Schema):
    corporation: dict | None = None


class AllianceAdmin(Schema):
    alliance: dict | None = None


class TopPilotSchema(Schema):
    character_id: int
    character_name: str
    main_name: str | None = None
    count: int  # kills or deaths
    total_value: int | float


class CombatStatsResponse(Schema):
    total_kills: int
    active_pvpers: int
    destroyed_isk: int | float
    lost_isk: int | float
    top_attackers: list[TopPilotSchema]
    top_victims: list[TopPilotSchema]


class CombatSummaryResponse(Schema):
    """Lightweight summary: counters + ISK totals only. Fast to compute."""

    total_kills: int
    active_pvpers: int
    destroyed_isk: int | float
    lost_isk: int | float


class TopPilotsResponse(Schema):
    """Top-N pilot list (attackers OR victims). Returned by dedicated endpoints."""

    pilots: list[TopPilotSchema]


class HallEntrySchema(Schema):
    killmail_id: int
    char_id: int
    char_name: str
    ship_id: int = 0
    ship_name: str = "Unknown"
    victim_ship_id: int = 0
    victim_ship_name: str = "Unknown"
    total_value: int | float
    damage_done: int = 0
    zkb_link: str


class HallResponseSchema(Schema):
    hall_of_fame: list[HallEntrySchema]
    hall_of_shame: list[HallEntrySchema]


class KillmailItemSchema(Schema):
    killmail_id: int
    killmail_date: str
    victim_id: int
    victim_name: str
    victim_ship_id: int
    victim_ship_name: str
    total_value: int | float
    solar_system_id: int = 0
    solar_system_name: str = "Unknown"
    security_status: float = 0.0
    pilot_count: int
    final_blow_id: int = 0
    final_blow_name: str = "Unknown"
    is_loss: bool = False
    zkb_link: str


class KillmailListResponse(Schema):
    killmails: list[KillmailItemSchema]
    total: int
    page: int = 1
    page_size: int = 50


class ModalSchema(Schema):
    """Schema for modal dialog data."""

    title: str
    text: str
    icon: str
    modal_id: str
    url: str
    color: str | None = None
    buttonText: str | None = None


class MenuLink(Schema):
    """
    Represents a link in the menu.
    """

    name: str
    link: str | None = None
    is_external: bool = False


class MenuCategory(MenuLink):
    """
    Represents a category in the menu, which can contain multiple links.
    """

    links: list[MenuLink] = []


class MenuModalSchema(Schema):
    """Schema for menu modals."""

    modal: ModalSchema | None = None


class MenuSchema(Schema):
    """
    Schema for the overall menu, including links and modals.
    """

    left_links: list[MenuLink] = []
    right_links: list[MenuLink] = []
    modals: MenuModalSchema | None = None
