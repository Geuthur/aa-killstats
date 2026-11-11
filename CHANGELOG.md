# Changelog

## [In Development] - Unreleased

<!--
> [!NOTE]
>

> [!TIP]
>

> [!IMPORTANT]
>

> [!WARNING]
>

> [!CAUTION]
>

Section Order:

### Added
### Fixed
### Changed
### Removed
-->

### Added

- Optional extra `tests-allianceauth-development` (test packages plus the Alliance Auth 6 pre-release) and separate test settings in `testauth/settings/development/` for the tox environment `allianceauth-development` and `make tox-tests-development`; a non-blocking CI job "AA Development" runs it on Python 3.13 and 3.14

### Fixed

- [FIX] Compatibility with Alliance Auth 6 (pre-release): the `eveonline` migration dependencies of `0001_initial`, `0001_init_v2` and `0002_rename_killstatsaudit_corporationsaudit_and_more` now point to `0019_v5squash` (Alliance Auth 6 removed the older `eveonline` migrations, `0019_v5squash` exists in Alliance Auth 5 as well). Works with Alliance Auth 5 and 6.
- [FIX] Unified the capitalization of the pagination labels: "First Page", "Previous Page", "Next Page" and "Last Page".
- [FIX] Added the translation keys for the renamed pagination labels and other missing keys to the i18n files.
- Fixed the total below the killmail table staying in English in every language: it passed a text as plural `count`, so i18next found no translation.
- Fixed `make coverage` exiting with 0 when tests failed. The reports are still created, and the target now exits with the status of the test run, or with the status of `coverage report` if the tests passed.
- [FIX] Tests no longer share the Redis cache with other processes. `testauth/settings/local.py` gives each test run its own random cache `KEY_PREFIX`. Before, ESI responses cached by a running testauth instance on the same Redis were returned instead of the pook responses. Redis stays the cache backend because Alliance Auth needs `django_redis`.

### Changed

- [CHANGE] Tasks that call ESI retry on ESI outages and limits instead of failing, as in the other apps: `store_killmail`, `check_and_import_corporation_killmails_task` and `check_and_import_alliance_killmails_task` run with `bind=True` inside `retry_task_on_esi_error` from `killstats/providers.py`. They retry on the ESI error limit, bucket limits, HTTP 502/503/504, network errors and during the daily downtime (11:00 to 11:15 UTC, skipped with `DISABLE_DAILY_DOWNTIME_CHECK = True`), at most 3 times. Other ESI errors (for example 404 or 500) still fail the task. `fetch_solar_system_id_for_killmail` keeps its behavior: it skips ESI when the killmail bucket is low and returns `None` on errors, because `run_tracker_missing_data` picks up killmails without solar system again every 15 minutes. `killstats/errors.py` has the new `DownTimeError`.
- [CHANGE] The `AppLogger` is created only once in `killstats/providers.py`. `admin.py`, `signals.py`, `views.py`, the management commands `killstats_migrate_eveentity`, `killstats_sync_killmails` and `killstats_update_solar_systems`, `managers/general_manager.py` and `managers/killboardaudit_manager.py` import it with `from killstats.providers import logger` instead of building their own. `api/admin.py`, `api/killboard.py`, `killstats_delete_npc_killmails`, `models/general.py`, `models/killboard.py` and `models/killstatsaudit.py` created a logger they never used; it is removed there. Log records now carry the logger name `killstats.providers` instead of the module name; the `[Killstats]` prefix is unchanged.
- [CHANGE] `aa-geuthur-react` raised to `^1.3.0`. The package bundles its own translations and registers them with i18next through `AaReactProvider`, so `Main.tsx` lists only the namespace `translation`, the copies under `killstats/static/killstats/i18n/<lng>/aa-geuthur-react.json` are removed and `make react-copy-translations` no longer copies them. Translate on Weblate as before.
- [CHANGE] The language files in `frontend/i18n/<lng>/translation.json` hold only real translations as Weblate writes them, missing keys fall back to English. `i18next-scanner` now maintains only `en`; empty placeholders (including empty plural forms) were removed from all other languages.
- The GitHub workflows follow the template of the other apps: `autotester.yml` no longer tests Python 3.10 (end of life) and uses `actions-setup-redis@v1.60.0`; `pypi.yml`, `release.yml` and `dependabot.yml` are identical to the template.
- The minimum Python version is now 3.11 (`requires-python`, classifiers and the tox matrix).
- The frontend uses the shared React base from the npm package [`aa-geuthur-react`](https://github.com/Geuthur/aa-geuthur-react) 1.2.0 instead of its own copies of the BaseTable stack, `BaseModal`, loaders, menu, utils, table styles and ESLint rule. The killmail table keeps the server-side pagination, the `keepPreviousData` dimming and the row colors. The table footer follows the layout of the package (page size, status and paging next to each other, stacked on phones).
- The entry files follow the template of the other apps: `App.tsx` and `main.tsx` became `Routing.tsx` and `Main.tsx` with `constants.ts` for `AppName` and `ProjectName`. `Routing.tsx` wraps the app in `AaReactProvider`, and `index.css` imports `aa-geuthur-react/styles.css` first, so the styles land in the CSS file the template loads. The pages use `AuthBase` of the package with `fluidOnSmallScreens`, so the container is 640 px to 1280 px wide and shrinks with the screen on phones.
- `apiClient` is `createApiClient<paths>()`, the query keys extend the `queryKeys` of the package, and the killboard page reads the user with `useUserData()`. The tests load `setupTests.ts` and no longer mock `useTranslation` or import `jest-dom` themselves.
- The API schemas `MenuLink`, `MenuSchema` and `UserData` follow the types of `aa-geuthur-react`: `MenuLink` has the optional `badge` and `has_errors`. The `menu/` and `user/` responses stay the same.
- Large ISK and kill numbers use `formatCompactNumber` of the package instead of the own `formatNumber`. The display stays the same.
- The killmail table now uses the shared `BaseTable` with server-side pagination, the `aa-table` styles and the shared footer. Kill and loss row colors, the total count and the page size of 250 stay.
- The killmail table keeps the current rows dimmed and locked while the next page or filter loads, instead of showing the loader each time.
- Replaced `pook` with `pookx` in the test dependencies and removed the custom `httpx2` pook interceptor, which `pookx` now provides.
- Renamed the package constant `__killmail_operations__` to `__operations__` in `killstats/__init__.py`, so it matches the other apps. The operations stay the same.
- Aligned `killstats/tests/__init__.py` with the shared test case class of the other apps. `AuthTestCase` no longer sets the unused `self.request`, and the type hints and extra docstring were dropped. No test changes were needed.

### Removed

- Removed the unused dependencies `tailwindcss` and `@tailwindcss/vite`. The plugin was never enabled, so the Tailwind classes in the components had no effect. They were removed or replaced by Bootstrap utilities.
- Removed the copies of the shared components, utils, table styles and the ESLint rule from `frontend/`, and the unused `MenuCategory`, `MenuModalSchema` and `ModalSchema` API schemas together with the unused `modals` field of the menu.
- Removed 31 translation keys the frontend no longer uses, including some with German source text.

<!-- Your changes go here -->

## [4.0.1] - 01.10.2026

## [4.0.0] - 01.10.2026

> [!IMPORTANT]
>
> This Release has changed the Task Structure.
> Therefore, add the following new task to ensure that the killmails continue to be updated

```python
if "killstats" in INSTALLED_APPS:
    CELERYBEAT_SCHEDULE["Killstats :: Check for Killmails"] = {
        "task": "killstats.tasks.run_tracker_zkb",
        "schedule": crontab(minute="*/1"),
    }
    CELERYBEAT_SCHEDULE["Killstats :: Check for Missing Killmail Data"] = {
        "task": "killstats.tasks.run_tracker_missing_data",
        "schedule": crontab(minute="*/15"),
    }
```

> [!CAUTION]
>
> Please note that this release involves structural dependency changes.
> Therefore, the command `killstats_migrate_old_killmails` is no longer available

### Added

#### Performance & Database Optimization

- **Index-Optimized Date Range Queries**: Migrated from SQL date extraction functions (`__year`/`__month`) to index-backed range queries (`gte`/`lt` on `killmail_date`), enabling full B-tree composite index scans across millions of killmails.
- **Composite Database Indexes**: Added composite indexes on `Killmail` (`km_date_idx`, `km_corp_loss_idx`, `km_ally_loss_idx`, `km_corp_val_idx`, `km_ally_val_idx`, `km_val_desc_idx`, `km_system_idx`) and `Attacker` (`att_km_final_blow_idx`) to drastically reduce query latency.
- **Server-Side Pagination & Two-Phase Loading**: Implemented high-performance database-level `LIMIT`/`OFFSET` pagination; detailed records (victims, ships, participants, final blows) are only fetched for the current page slice.
- **N+1 Query Elimination**: Resolved N+1 query bottlenecks via native Django `SolarSystem.objects.in_bulk(...)` bulk lookups.

#### Backend API (Django Ninja V2)

- **RESTful Query Parameter Filtering**: Converted API routes from static URL path dates to flexible Django Ninja `FilterSchema` query parameters (`DateRangeFilter`, `TopPilotsFilter`, `HallFilter`, `KillmailFilter`).
- **Manager & QuerySet Encapsulation**: Cleanly encapsulated entity lookups (`Attacker.objects.for_entity(...)`, `Killmail.objects.for_victim_entity(...)`) and pagination logic (`Killmail.objects.get_paged_ids(...)`) directly within model managers.
- **Modular Endpoints**: Decomposed monolithic endpoints into lightweight, parallel endpoints (`/stats/v2/summary/`, `/stats/v2/attackers/`, `/stats/v2/victims/`, `/hall/v2/`, `/killmails/`).

#### Frontend (Modern React Framework)

- **Vite & TypeScript SPA**: Brand-new Single Page Application frontend built with React 19, TypeScript, and Vite.
- **TanStack Query & State Management**: Parallel data fetching with automated caching, background updates, and URL query state persistence via `nuqs`.
- **Interactive UI Components**: Purpose-built components for killboard stats, TanStack Table with server-side pagination, Hall of Fame & Shame, Top Pilots modal, and tooltips with direct zKillboard links.
- **Full Localization & Test Suite**: Multi-language i18n support (EN/DE) with `react-i18next` and unit testing via Vitest and React Testing Library.

#### CSS Framework & Theme Integration

- **Isolated Styling for Alliance Auth**: Conflict-free utility design system (`ks-*` classes) designed to seamlessly integrate with all standard Alliance Auth themes.
- **Vowra Dark Theme Aesthetic**: Sleek EVE-inspired dark interface featuring glassmorphism (`backdrop-blur`), subtle glowing gradients, and styled rank badges (Gold/Silver/Bronze).

### Changed

- Made the React-based Killboard V2 the default view across the application.
- Increased backend test coverage above 83% with `AuthTestCase` and network isolation (`pook`).
- Modernized `KillmailBody` to Pydantic v2 `BaseModel`.

### Removed

- Deprecated server-side Django template views (`killboard.html`, `corporation_admin.html`, `alliance_admin.html`).
- Obsolete V1 Ninja endpoints (`/killmail/month/...`, `/halls/month/...`, `/stats/top/10/...`, `/stats/all/...`).
- Legacy helper functions and unused modules (`_date_filters_*`, `_entity_*_q`, `account_manager.py`, `service.py`, `sync.py`).
- Management command `killstats_migrate_old_killmails`.

## [3.0.1] - 28.05.2026

### Fixed

- Import Error for Exception

## [3.0.0] - 2026-05-09

> [!IMPORTANT]
>
> This Release needs at least Alliance Auth v5
> Please make sure to update your Alliance Auth before you install this APP

### Added

- Compatibility to Alliance Auth v5

### Removed

- Compatibility to Alliance Auth v4

## [2.0.6] - 2026-05-08

### Added

- Python 3.13 Support

### Changed

- Optimized EVE_SDE Migration Process for more clarity

## [2.0.5] - 2026-04-05

### Fixed

- No Character Portrait in Hall of Fame

### Changed

- Optimized Manager Pylance
- Store KM Log Level to debug

## [2.0.4] - 2026-04-04

### Fixed

- Killmail Processing not Saving Killmails

## [2.0.3] - 2026-03-31

> [!WARNING]
>
> If you updating from older version then v2 Please read the Notes from Version v2

### Added

- charlink hook and implement character audit functionality

### Changed

- Optimize killmail processing and update test data structure

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
[2.0.3]: https://github.com/Geuthur/aa-killstats/compare/v2.0.2...v2.0.3 "2.0.3"
[2.0.4]: https://github.com/Geuthur/aa-killstats/compare/v2.0.3...v2.0.4 "2.0.4"
[2.0.5]: https://github.com/Geuthur/aa-killstats/compare/v2.0.4...v2.0.5 "2.0.5"
[2.0.6]: https://github.com/Geuthur/aa-killstats/compare/v2.0.5...v2.0.6 "2.0.6"
[3.0.0]: https://github.com/Geuthur/aa-killstats/compare/v2.0.6...v3.0.0 "3.0.0"
[3.0.1]: https://github.com/Geuthur/aa-killstats/compare/v3.0.0...v3.0.1 "3.0.1"
[4.0.0]: https://github.com/Geuthur/aa-killstats/compare/v3.0.1...v4.0.0 "v4.0.0"
[4.0.1]: https://github.com/Geuthur/aa-killstats/compare/v4.0.0...v4.0.1 "v4.0.1"
[in development]: https://github.com/Geuthur/aa-killstats/compare/v4.0.1...HEAD "In Development"
