# Changelog

## [In Development] - Unreleased

<!--
Section Order:

### Added
### Fixed
### Changed
### Removed
-->

## [2.0.2] - 2026-03-23

> [!WARNING]
>
> If you updating from older version then v2 Please read the Notes from Version v2

### Added

- AAv5 Test Enviroment

### Fixed

- update ItemType retrieval to use 'id'

## [2.0.1] - 2026-03-11

> [!WARNING]
>
> If you updating from older version then v2 Please read the Notes from Version v2

### Fixed

- update victim ship retrieval to use ItemType model

## [2.0.0] - 2026-03-04

> [!WARNING]
>
> Please note that this release involves structural dependency changes.
> To avoid any service disruptions, it is essential to read the update manual prior to performing the upgrade.

### Update Instructions

After isntalling this version, you need to modify `INSTALLED_APPS` in your `local.py`

```python
INSTALLED_APPS = [
    # other apps
    "eve_sde",  # only if it not already existing
    "killstats",
    # other apps?
]

# This line is right below the `INSTALLED_APPS` list, if not already exist!
INSTALLED_APPS = ["modeltranslation"] + INSTALLED_APPS
```

Add the following new task to ensure the SDE data is kept up to date.

```python
if "eve_sde" in INSTALLED_APPS:
    # Run at 12:00 UTC each day
    CELERYBEAT_SCHEDULE["EVE SDE :: Check for SDE Updates"] = {
        "task": "eve_sde.tasks.check_for_sde_updates",
        "schedule": crontab(minute="0", hour="12"),
    }
```

Due to the new R2Z2 endpoints, we need to replace the existing Celery task. Therefore, add the following new task to ensure that the killmails continue to be updated

```python
if "killstats" in INSTALLED_APPS:
    CELERYBEAT_SCHEDULE["Killstats :: Check for Killmails"] = {
        "task": "killstats.tasks.run_zkb_r2z2",
        "schedule": crontab(minute="*/1"),
    }
```

> [!IMPORTANT]
> This is only for installed Killstats Enviroment
> The Migration can take long if you have a big Killstats DB
> You need to have eveuniverse installed during the migration otherwise it will not migrate the old entries.

After running migrations, make sure to run the following commands to import the SDE data into your database.

```shell
python manage.py esde_load_sde
```

Restart your Auth via `supervisor` after running these commands

### Added

- `django-eveonline-sde` dependency

### Changed

- Replace `django-eveuniverse` with `django-eveonline-sde`
- Migration to R2Z2 endpoints, as Redis will be removed on May 31
- Updated Translations

### Removed

- `allianceauth-app-utils` dependency
- `django-eveuniverse` dependency

## [1.0.4] - 2025-12-01

### Added

- `get_single_killmail` test
- Discord Link to `README.md`

### Changed

- Killmails are now fetched from ESI instead of zKB.

### Removed

- `_create_from_openapi` function

## [1.0.3] - 2025-11-16

### Changed

- Downgrade `allianceauth-app-utils` to `>=1.30`

## [1.0.2] - 2025-11-15

### Added

- Translation

### Changed

- Updated CONTRIBUTING.md

### Fixed

- OpenAPI3 Killmails not serializable [#71](https://github.com/Geuthur/aa-killstats/issues/71)

## [1.0.1] - 2025-11-13

### Changed

- Updated dependencies
  - `allianceauth-app-utils` to `>=2b2`
  - `allianceauth` to `>=4.10,<5`
  - `django-esi` to `8,<9`
  - `django-eveuniverse` to `>=1.6`

### Removed

- csrf arg from `django-ninja`
- `django-ninja` dependency pin `<1.5`

## [1.0.0] - 13.11.2025

### Added

- Temporary pin `django-ninja` to `django-ninja<=1.5`
  - https://github.com/vitalik/django-ninja/pull/1524

### Changed

- renamed `create_attackers` to `get_or_create_attackers`
- Migrated OpenAPI3 ESI Client for single Killmail
- update var naming in `create_from_killmail`
- use Django Commands for old Killmail migration

## [0.6.2] - 14.10.2025

### Added

- Automatic Release workflow

### Changed

- Optimized ESI Status endpoint

## [0.6.1] - 08.10.2025

### Changed

- Redis Lock System to avoid hammering ESI Endpoint

As of August 2025 zKB redis has changed their request limitations [see here](https://github.com/zKillboard/RedisQ/blob/master/README.md#limitations)

## [0.5.6-0.6.0] - 26.09.2025

### Fixed

- `run_zkb_reids` Task endless lock

### Added

- 429: Too Many Requests Handler
- timeout for redis lock
- Makefile System
- Translations

### Changed

- while to for to avoid infinite loops
- [moved killmail_core to helpers & renamed to killmail](https://github.com/Geuthur/aa-killstats/commit/4231d846e7683790d8080a5c640a524ef3a419b1)
- [Refactor Logger System](https://github.com/Geuthur/aa-killstats/commit/b8590ffa9b377e80b17ce629f6cabd2b7090052e)

### Removed

- raise_for_status()
- [Cache Buster](https://github.com/Geuthur/aa-killstats/commit/16a81c519a8c3db46af23d58eabf36261d1fb866)

## [0.5.5] - 11.07.2025

## Added

- dependabot
- `django-esi` dependency

## Changed

- Use `django-esi` new User Agent Guidelines

## [0.5.4] - 05.07.2025

### Changed

- Minimum dependencies
  - allianceauth>=4.8.0

### Fixed

- Wrong Static path

## [0.5.3] - 07.05.2025

### Fixed

- New zKB Redis URL

### Added

- Add Killmail to Killstats System

> [!IMPORTANT]
> We Changes the Killmail Fetch System please Read the README!
> You need to ADD the KILLSTATS_QUEUE_ID to your local.py

## [0.5.2] - 28.04.2025

### Added

- Cache Busting by [@ppfeufer](https://github.com/ppfeufer)
- Year Dropdown Menu

### Changed

- Refactor Stats System
  - Optimized Code
  - Removed unnecessary Code
  - Improved Query
  - Make it more readable
- Refactor Account Manager
  - Optimized Code
- Refactor Killstats
  - Removed Multi View
  - Use EveEntity functions for portrait instead of create own
  - Removed Bulk Fetch and use Redes from zKB
  - Refactor Tasks
- Template
  - Optimized CSS
  - Update Modal System
- Java
  - Refactor Killstats
  - Moved common scripts to own file

### Removed

- Killmail Model
  - evaluate_victim_id
  - evaluate_portrait
  - get_ship_image_url
  - get_image_url

## [0.5.1] - 2024-11-22

### Added

- Top 10 Information Sheet
- Explanation MD
- Cache System (10 min) default, can be change with `KILLBOARD_API_CACHE_LIFETIME`

### Changed

- All Stats Types have now own Endpoint
- Top Kill & Top Loss linked to killmail instead of character page
- Database changed killmail_id, weapon_item_id, victim_alliance_id, victim_corporation_id, victim_region_id, victim_solar_system_id from PositiveBigIntegerField to PositiveIntegerField
- Database changed killmail_date from Datetime(6) to Datetime(0)

### Fixed

- Long loading time for Stats Dashboard
- Wrong Top Ship Killcount (counted for each ship in one killmail)
- Hall of Fame not showing on Alliance Overview
- NPC Corporation should not be able to be added to Killstats
- Alliance not updating after Adding it

## [0.5.0] - 2024-10-14

> [!IMPORTANT]
> With the new Version we need to delete all Killmails.
> The Migration can take a while if Killmail DB is big
> We prefer to clear the Killstats `killstats_killmail`

### Added

- Added Attacker model isntead of Json Field
- Log timing for performance tests

### Chamged

- Installation Description for README
- Get EVE Data from django eveuniverse
- Significant Performance boost in Stats Process
- Killmails are now create atomic
- Killmail Datatable Search supports now Type, Character, Total Value, Date
- Design Improvments

### Fixed

- API Fetch Error if Ship not exist
- Overview Action button title is edit instead of show
- Tasks create killmails that already exists
- zKB Cache cached wrong on first 2 pages

### Removed

- EveEntity model
- Stats Manager now handled directly from QuerySet
- Attacker JSON Field from Killmail
- Temporarily removed filter Hall of Fame accept only 1 kill per Character cause performance issues
- Corp Utils, CorpStats Two support not needed anymore

## [0.1.9] - 2024-09-05

### Fixed

- No Permission occurs if Data is Empty

### Moved

- Killstats Stats moved ip and Header moved down to Hall of Fame Header

## [0.1.8] - 2024-08-16

### Performance

- Optimized Loading Times
- Optimized Database Querys

### Fixed

- Hall of Shame/Fame switch Tabs Bug
- Portrait System for Alliance,Corporation,Character
- Stats System

### Added

- Filters
  - Mining Barge
  - Exhumer
  - Industrial Command Ship
  - Capital Industrial Ship
- Alliance Killstats API
- AllianceAudit
- Alliance Overview
- Account Manager Class
- Killmail Fetch System with Datatable Feature

### Changed

- Refactor Killstats API
- Refactor Killstats Data Fetching System
- Refactor Killstats Javascript
- Refactor Killboard Manager
- Moved Mains & Alts Functions to Account Manager
- Renamed KillstatsAudit to CorporationAudit
- Moved Stats to own API
- Moved Hall of Fame/Shame to own API

### Removed

- Threshold Filter in Hall of Fame

## [0.1.7] - 2024-08-06

### Added

- Corporation Killstats Overview
- Single Lookup for each Corporation
- Killmail Database Corporations Filter

### Removed

- Hall of Fame/Shame Tab Display (in some cases it shows both)
- Classmethod attackers_mains & threshold
- Python 3.8, 3.8 Support

## [0.1.6] - 2024-07-20

### Fixed

- wrong id var in repr, icon_url

### Added

- Many Tests

### Changed

- EveEntity entity_id to eve_id

## [0.1.5] - 2024-07-08

### Fixed

- Add Corp doesn't work for admin_access
- Site Error on Char not exist
- Worst Ship shows Deployable losses

### Added

- is_mobile() to filter Deployable

### Changed

- Refactor Killboard Manager
- Killboard JS
- Structures now be handled by category id
- Structure Kills now also count for Hall of Fame
- Image Handling

### Removed

- STRUCTURE Var from app_settings

## [0.1.4] - 2024-07-04

### Added

- Loading Animation before finish page

### Changed

- Refactoring Killboard.js
- Moved Month Menu to top

### Removed

- Some unnecessary Text

## [0.1.0-0.1.3] - 2024-06-28

### Fixed

- Crontab period 1 minute...

### Changed

- Moved JS to File

### Added

- Initial public release

[1.0.1]: https://github.com/Geuthur/aa-killstats/compare/v1.0.0...v1.0.1 "1.0.1"
[1.0.2]: https://github.com/Geuthur/aa-killstats/compare/v1.0.1...v1.0.2 "1.0.2"
[1.0.3]: https://github.com/Geuthur/aa-killstats/compare/v1.0.2...v1.0.3 "1.0.3"
[1.0.4]: https://github.com/Geuthur/aa-killstats/compare/v1.0.3...v1.0.4 "1.0.4"
[2.0.0]: https://github.com/Geuthur/aa-killstats/compare/v1.0.4...v2.0.0 "2.0.0"
[2.0.1]: https://github.com/Geuthur/aa-killstats/compare/v2.0.0...v2.0.1 "2.0.1"
[2.0.2]: https://github.com/Geuthur/aa-killstats/compare/v2.0.1...v2.0.2 "2.0.2"
[in development]: https://github.com/Geuthur/aa-killstats/compare/v2.0.2...HEAD "In Development"
