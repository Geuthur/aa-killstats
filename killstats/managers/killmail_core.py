# Standard Library
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

# Third Party
import requests
from dacite import DaciteError, from_dict
from redis.exceptions import LockError

# Django
from django.core.cache import cache
from django.utils.dateparse import parse_datetime

# Alliance Auth (External Libs)
from app_utils.allianceauth import get_redis_client
from app_utils.json import JSONDateTimeDecoder, JSONDateTimeEncoder

# AA Voices of War
from killstats import __title__, __version__
from killstats.app_settings import (
    KILLBOARD_MAX_KILLMAILS_PER_RUN,
    KILLBOARD_STORAGE_LIFETIME,
    KILLBOARD_ZKB_CACHE_LIFETIME,
    STORAGE_BASE_KEY,
    ZKILLBOARD_API_URL,
)
from killstats.hooks import get_extension_logger
from killstats.providers import esi

logger = get_extension_logger(__name__)
USERAGENT = "killstats v{__version__}"

MAX_RETRIES = 3
RETRY_DELAY = 3


class KillboardException(Exception):
    """Exception from Killboard"""


class KillmailDoesNotExist(KillboardException):
    """Killmail does not exist in storage."""


@dataclass
class _KillmailBase:
    """Base class for all Killmail."""

    def asdict(self) -> dict:
        """Return this object as dict."""
        return asdict(self)


@dataclass
class _KillmailCharacter(_KillmailBase):
    ENTITY_PROPS = [
        "character_id",
        "corporation_id",
        "alliance_id",
        "faction_id",
        "ship_type_id",
    ]

    character_id: int | None = None
    corporation_id: int | None = None
    alliance_id: int | None = None
    faction_id: int | None = None
    ship_type_id: int | None = None


@dataclass
class KillmailVictim(_KillmailCharacter):
    """A victim on a killmail."""

    damage_taken: int | None = None


@dataclass
class KillmailAttacker(_KillmailCharacter):
    """An attacker on a killmail."""

    ENTITY_PROPS = _KillmailCharacter.ENTITY_PROPS + ["weapon_type_id"]

    damage_done: int | None = None
    is_final_blow: bool | None = None
    security_status: float | None = None
    weapon_type_id: int | None = None


@dataclass
class KillmailPosition(_KillmailBase):
    "A position for a killmail."
    x: float | None = None
    y: float | None = None
    z: float | None = None


@dataclass
class KillmailZkb(_KillmailBase):
    """A ZKB entry for a killmail."""

    location_id: int | None = None
    hash: str | None = None
    fitted_value: float | None = None
    dropped_value: float | None = None
    destroyed_value: float | None = None
    total_value: float | None = None
    points: int | None = None
    is_npc: bool | None = None
    is_solo: bool | None = None
    is_awox: bool | None = None


@dataclass
class KillmailManager(_KillmailBase):
    """Killmail Manager"""

    _STORAGE_BASE_KEY = "killboard_storage_killmail_"

    id: int
    time: datetime
    victim: KillmailVictim
    attackers: list[KillmailAttacker]
    position: KillmailPosition
    zkb: KillmailZkb
    solar_system_id: int | None = None

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id})"

    def asjson(self) -> str:
        """Convert killmail into JSON data."""
        return json.dumps(asdict(self), cls=JSONDateTimeEncoder)

    @staticmethod
    def get_killmail_data_bulk(
        base_url: str, max_entries_per_bulk: int = KILLBOARD_MAX_KILLMAILS_PER_RUN
    ):
        """Get kill data bulk from zKillboard"""
        # TODO Maybe another way to get the data?
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Killmail

        killmail_list = []
        try:
            for page in range(1, 20):
                result = KillmailManager._fetch_page_data(base_url, page)
                if result is None:
                    continue
                killmail_ids = [data["killmail_id"] for data in result]
                existing_killmail_ids = Killmail.objects.filter(
                    killmail_id__in=killmail_ids
                ).values_list("killmail_id", flat=True)
                new_killmails = [
                    data
                    for data in result
                    if data["killmail_id"] not in existing_killmail_ids
                ]

                for data in new_killmails:
                    killmail_dict = KillmailManager._process_killmail_data(data)
                    if killmail_dict:
                        killmail_list.append(killmail_dict)
                        if len(killmail_list) >= max_entries_per_bulk:
                            return killmail_list
        # pylint: disable=broad-exception-caught
        except Exception as exc:
            logger.error("Failed to fetch killmails: %s", exc, exc_info=True)
        return killmail_list

    @staticmethod
    def _fetch_page_data(base_url, page):
        cache_key = f"zkb_page_cache_{base_url}_{page}"
        cached_zkb = cache.get(cache_key)
        if cached_zkb is not None:
            return cached_zkb

        redis = get_redis_client()

        retries = 0
        while retries < MAX_RETRIES:
            try:
                # Ensure that you dont spam zKB Requests
                with redis.lock(
                    KillmailManager.lock_key(), sleep=3, blocking_timeout=5
                ):
                    logger.debug("Fetching %s page %s from zKillboard", base_url, page)
                    url = f"{base_url}page/{page}/"
                    headers = {
                        "User-Agent": USERAGENT,
                        "Content-Type": "application/json",
                        "Accept-Encoding": "gzip",
                    }
                    request_result = requests.get(url=url, headers=headers)
                    request_result.raise_for_status()
                    # Only refresh page 1-3 cause other pages are not changing (normally)
                    if page > 3:
                        timeout_value = KILLBOARD_ZKB_CACHE_LIFETIME
                        cache.set(
                            key=cache_key,
                            value=request_result.json(),
                            timeout=timeout_value,
                        )
                    # Sleep to prevent spamming zKB
                    time.sleep(1)
                    return request_result.json()
            except LockError:
                logger.debug("Lock is already in use. Retrying...")
                retries += 1
                time.sleep(RETRY_DELAY)
            except requests.RequestException as exc:
                logger.warning("Request failed: %s", exc, exc_info=True)
                raise ValueError(str(exc)) from exc
        logger.error("Failed to fetch page %s from zKillboard", page)
        return None

    @staticmethod
    def _process_killmail_data(data):
        try:
            killmail_id = data["killmail_id"]
            killmail_hash = data["zkb"]["hash"]
            esi_killmail = esi.client.Killmails.get_killmails_killmail_id_killmail_hash(
                killmail_id=killmail_id, killmail_hash=killmail_hash
            ).result()
            esi_killmail["killmail_time"] = esi_killmail["killmail_time"].strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            return {"killID": killmail_id, "killmail": esi_killmail, "zkb": data["zkb"]}
        # pylint: disable=broad-exception-caught
        except Exception as exc:
            logger.error("Killmail can't fetch %s", exc)
            return None

    # pylint: disable=too-many-locals
    @classmethod
    def get_single_killmail(cls, killmail_id: int):
        """Get kill data from zKillboard"""
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Killmail

        cache_key = f"{STORAGE_BASE_KEY}_KILLMAIL_{killmail_id}"
        killmail_json = cache.get(cache_key)
        if killmail_json:
            return KillmailManager.from_json(killmail_json)

        logger.debug("Fetching killmail %s from zKillboard", killmail_id)

        url = f"{ZKILLBOARD_API_URL}killID/{killmail_id}/"
        headers = {"User-Agent": USERAGENT, "Content-Type": "application/json"}
        request_result = requests.get(url=url, headers=headers, timeout=5)

        try:
            request_result.raise_for_status()
            zkb_killmail = request_result.json()[0]
        except requests.HTTPError as exc:
            error_str = str(exc)

            logger.warning(
                msg=f"Unable to get killmail details from zKillboard. Error: {error_str}",
                exc_info=True,
            )

            raise ValueError(error_str) from exc
        except requests.Timeout as exc:
            error_str = str(exc)

            logger.warning(msg="Connection to zKillboard timed out …")

            raise ValueError(error_str) from exc

        try:
            killmail_id = zkb_killmail["killmail_id"]
            killmail_hash = zkb_killmail["zkb"]["hash"]

            # Überprüfe, ob die Killmail bereits in der Datenbank existiert
            existing_killmail = Killmail.objects.filter(killmail_id=killmail_id).first()

            if existing_killmail:
                logger.debug("Killmail %s exists already..", killmail_id)
                return None

            esi_killmail = esi.client.Killmails.get_killmails_killmail_id_killmail_hash(
                killmail_id=killmail_id, killmail_hash=killmail_hash
            ).results()
        except Exception as exc:
            raise ValueError("Invalid Kill ID or Hash.") from exc

        esi_killmail["killmail_time"] = esi_killmail["killmail_time"].strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        killmail_dict = {
            "killID": killmail_id,
            "killmail": esi_killmail,
            "zkb": zkb_killmail["zkb"],
        }
        killmail = cls._create_from_dict(killmail_dict)
        if killmail:
            cache.set(key=cache_key, value=killmail.asjson())
        return killmail

    def save(self) -> None:
        """Save this killmail to temporary storage."""
        cache.set(
            key=self._storage_key(self.id),
            value=self.asjson(),
            timeout=KILLBOARD_STORAGE_LIFETIME,
        )
        logger.debug("Cache created for %s", self.id)

    def delete(self) -> None:
        """Delete this killmail from temporary storage."""
        cache.delete(self._storage_key(self.id))

    def create_names_bulk(self, eve_ids: list):
        # pylint: disable=import-outside-toplevel
        from eveuniverse.models import EveEntity

        if len(eve_ids) > 0:
            EveEntity.objects.bulk_create_esi(eve_ids)
            return True
        return False

    @staticmethod
    def get_ship_name(ship_type: int):
        # pylint: disable=import-outside-toplevel
        from eveuniverse.models import EveType

        ship_name, new_entry = EveType.objects.get_or_create_esi(id=ship_type)
        if new_entry:
            logger.debug("Kllboard Manager Ship: %s added", ship_name.name)
        return ship_name

    @staticmethod
    def get_entity_name(eve_id: int):
        # pylint: disable=import-outside-toplevel
        from eveuniverse.models import EveEntity

        entity, new_entry = EveEntity.objects.get_or_create_esi(id=eve_id)
        if new_entry:
            logger.debug("Kllboard Manager EveName: %s added", entity.name)
        return entity

    @staticmethod
    def get_region_id(solar_system: int):
        # pylint: disable=import-outside-toplevel
        from eveuniverse.models import EveSolarSystem

        solar_system, new_entry = EveSolarSystem.objects.get_or_create_esi(
            id=solar_system
        )
        region_id = solar_system.eve_constellation.eve_region
        if new_entry:
            logger.debug("%s added to System", region_id.name)
        return region_id.id

    def create_attackers(self, killmail, killmanager):
        # pylint: disable=import-outside-toplevel
        from killstats.models.killboard import Attacker

        for attacker in killmanager.attackers:
            character = None
            if attacker.character_id:
                character = self.get_entity_name(attacker.character_id)

            corporation = None
            if attacker.corporation_id:
                corporation = self.get_entity_name(attacker.corporation_id)

            alliance = None
            if attacker.alliance_id:
                alliance = self.get_entity_name(attacker.alliance_id)

            ship = None
            if attacker.ship_type_id:
                ship = self.get_ship_name(attacker.ship_type_id)

            Attacker.objects.get_or_create(
                killmail=killmail,
                character=character,
                corporation=corporation,
                alliance=alliance,
                defaults={
                    "ship": ship,
                    "damage_done": attacker.damage_done,
                    "final_blow": attacker.is_final_blow,
                    "security_status": attacker.security_status,
                    "weapon_type_id": attacker.weapon_type_id,
                },
            )
        return True

    @classmethod
    def get(cls, cache_id: int) -> "KillmailManager":
        """Fetch a killmail from temporary storage."""
        data = cache.get(key=cls._storage_key(cache_id))
        if not data:
            raise KillmailDoesNotExist(
                f"Killmail with ID {cache_id} does not exist in storage."
            )
        return cls.from_json(data)

    @classmethod
    def _storage_key(cls, cache_id: int) -> str:
        return cls._STORAGE_BASE_KEY + str(cache_id)

    @staticmethod
    def lock_key() -> str:
        """Key used for lock operation on Redis."""
        return f"{__title__.upper()}_REDISQ_LOCK"

    @classmethod
    def from_dict(cls, data: dict) -> "KillmailManager":
        """Create new object from dictionary."""
        try:
            return from_dict(data_class=KillmailManager, data=data)
        except DaciteError as ex:
            logger.error("Failed to convert dict to %s", type(cls), exc_info=True)
            raise ex

    @classmethod
    def from_json(cls, json_str: str) -> "KillmailManager":
        """Create new object from JSON data."""
        return cls.from_dict(json.loads(json_str, cls=JSONDateTimeDecoder))

    @classmethod
    def _extract_victim_and_position(cls, killmail_data: dict):
        victim = KillmailVictim()
        position = KillmailPosition()
        if "victim" in killmail_data:
            victim_data = killmail_data["victim"]
            params = {}
            for prop in KillmailVictim.ENTITY_PROPS + ["damage_taken"]:
                if prop in victim_data:
                    params[prop] = victim_data[prop]

            victim = KillmailVictim(**params)

            if "position" in victim_data:
                position_data = victim_data["position"]
                params = {}
                for prop in ["x", "y", "z"]:
                    if prop in position_data:
                        params[prop] = position_data[prop]

                position = KillmailPosition(**params)

        return victim, position

    @classmethod
    def _extract_attackers(cls, killmail_data: dict) -> list[KillmailAttacker]:
        attackers = []
        for attacker_data in killmail_data.get("attackers", []):
            params = {}
            for prop in KillmailAttacker.ENTITY_PROPS + [
                "damage_done",
                "security_status",
            ]:
                if prop in attacker_data:
                    params[prop] = attacker_data[prop]

            if "final_blow" in attacker_data:
                params["is_final_blow"] = attacker_data["final_blow"]

            attackers.append(KillmailAttacker(**params))
        return attackers

    @classmethod
    def _extract_zkb(cls, package_data):
        if "zkb" not in package_data:
            return KillmailZkb()

        zkb_data = package_data["zkb"]
        params = {}
        for prop, mapping in (
            ("locationID", "location_id"),
            ("hash", None),
            ("fittedValue", "fitted_value"),
            ("droppedValue", "dropped_value"),
            ("destroyedValue", "destroyed_value"),
            ("totalValue", "total_value"),
            ("points", None),
            ("npc", "is_npc"),
            ("solo", "is_solo"),
            ("awox", "is_awox"),
        ):
            if prop in zkb_data:
                if mapping:
                    params[mapping] = zkb_data[prop]
                else:
                    params[prop] = zkb_data[prop]

        return KillmailZkb(**params)

    @classmethod
    def _create_from_dict(cls, package_data: dict) -> Optional["KillmailManager"]:
        """creates a new object from given dict.
        Needs to confirm with data structure returned from ZKB RedisQ
        """

        killmail = None
        if "killmail" in package_data:
            killmail_data = package_data["killmail"]
            victim, position = cls._extract_victim_and_position(killmail_data)
            attackers = cls._extract_attackers(killmail_data)
            zkb = cls._extract_zkb(package_data)

            params = {
                "id": killmail_data["killmail_id"],
                "time": parse_datetime(killmail_data["killmail_time"]),
                "victim": victim,
                "position": position,
                "attackers": attackers,
                "zkb": zkb,
            }
            if "solar_system_id" in killmail_data:
                params["solar_system_id"] = killmail_data["solar_system_id"]

            killmail = KillmailManager(**params)

        return killmail
