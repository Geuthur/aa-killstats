# Changelog

## \[0.5.0\] - 2024-09-26

> \[!IMPORTANT\]
> With the new Version we need to delete all Killmails.
> The Migration can take a while if Killmail DB is big
> We prefer to clear the Killstats Killmail table

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
- Corp Utils, CorpStats Two support

## \[0.1.9\] - 2024-09-05

### Fixed

- No Permission occurs if Data is Empty

### Moved

- Killstats Stats moved ip and Header moved down to Hall of Fame Header

## \[0.1.8\] - 2024-08-16

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

## \[0.1.7\] - 2024-08-06

### Added

- Corporation Killstats Overview
- Single Lookup for each Corporation
- Killmail Database Corporations Filter

### Removed

- Hall of Fame/Shame Tab Display (in some cases it shows both)
- Classmethod attackers_mains & threshold
- Python 3.8, 3.8 Support

## \[0.1.6\] - 2024-07-20

### Fixed

- wrong id var in repr, icon_url

### Added

- Many Tests

### Changed

- EveEntity entity_id to eve_id

## \[0.1.5\] - 2024-07-08

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

## \[0.1.4\] - 2024-07-04

### Added

- Loading Animation before finish page

### Changed

- Refactoring Killboard.js
- Moved Month Menu to top

### Removed

- Some unnecessary Text

## \[0.1.0-0.1.3\] - 2024-06-28

### Fixed

- Crontab period 1 minute...

### Changed

- Moved JS to File

### Added

- Initial public release
