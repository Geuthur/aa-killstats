# Changelog

## \[0.1.8\] - 2024-08-xx

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

### Changed

- Refactor get_main_alts
- Renamed KillstatsAudit to CorporationAudit
- Killstats Javascript

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
