# Git Commit & Changelog Guidelines

When suggesting or creating git commits and changelog entries for this repository, strictly adhere to the following conventions:

## 1. Commit Message Format

Use square bracket prefixes matching the project's changelog sections:

- **`[ADD]`**: New features, components, models, endpoints, or dependencies.
- **`[CHANGE]`**: Updates, refactoring, improvements, or dependency upgrades.
- **`[FIX]`**: Bug fixes and error resolutions.
- **`[REMOVED]`**: Deleted features, files, or deprecated options.

### Structure:

```text
[TAG] Short description (imperative, max 72 characters)

- Bullet points detailing what was added, changed, or fixed
- Affected components (pages, endpoints, models, hooks)
- Relevant behavioral notes or rationale
```

### Examples:

```text
[ADD] zKB Backend integration

- Add Celery tasks for fetching killmail stats from zKillboard
- Introduce ZkbStats model and database migrations
- Add helper functions in eveonline.py
```

```text
[FIX] Prevent double loading of session data

- Add check for active request state in useSessionData hook
- Resolve flickering on initial route mount
```

## 2. Changelog (`CHANGELOG.md`)

When updating `CHANGELOG.md`:

- Always place new entries under `## [In Development] - Unreleased`.
- If an `<!-- AI Changes -->` marker exists, place the entries directly in the relevant subsection below it.
- Group entries into matching sections respecting the standard section order:
  - `### Added` for `[ADD]`
  - `### Fixed` for `[FIX]`
  - `### Changed` for `[CHANGE]`
  - `### Removed` for `[REMOVED]`
- If a section does not exist yet under `## [In Development] - Unreleased`, create it respecting this order.
- Format entries as concise bullet points: `- Short summary of the change`.
- Keep entries clear, human-readable, and aligned with Keep a Changelog standards.
