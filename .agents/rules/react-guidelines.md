# React Development Guidelines

When working on frontend code in this repository, strictly adhere to the following rules:

## 1. Always Use `@/` Import Paths (Never Relative `./` or `../`)

- All internal project imports and exports must **always** use the `@/` path alias (which resolves to `frontend/src/`).
- Do **not** use relative imports such as `./` or `../`.

### Examples:

```typescript
// ❌ INCORRECT (relative paths)
import { SnapshotSelect } from './SnapshotSelect';
import { formatDate } from '../../Helpers/functions';
import BaseTable from '../BaseTable';
export { default as SnapshotButtons } from './SnapshotButtons';

// ✅ CORRECT (always use @/)
import { SnapshotSelect } from '@/Components/Tables/Snapshot/SnapshotSelect';
import { formatDate } from '@/Components/Helpers/functions';
import BaseTable from '@/Components/Tables/BaseTable';
export { default as SnapshotButtons } from '@/Components/Tables/Snapshot/SnapshotButtons';
```

## 2. Topic-Based Component Folders (under `Tables/`, etc.)

- Organize related subcomponents into dedicated topic folders (e.g. `Components/Tables/Snapshot/`).
- Keep components small, modular, and focused (e.g., `<SnapshotSelect />`, `<SnapshotButtons />`).
- Each folder should contain an `index.ts` file that re-exports components using `@/` path aliases.

### Example Structure:

```text
frontend/src/Components/Tables/
├── Snapshot/
│   ├── SnapshotSelect.tsx    # Dropdown selector component
│   ├── SnapshotButtons.tsx   # Action buttons component (Add/Delete)
│   └── index.ts              # Exports using @/ aliases
├── BaseTable.tsx
└── ...
```

## 3. Import Grouping & Ordering

Follow the project import order convention:

1. **React**:
   ```typescript
   import { useState, useMemo } from 'react';
   import { useParams } from 'react-router-dom';
   ```
1. **Third-Party Libraries**:
   ```typescript
   import { useQuery } from '@tanstack/react-query';
   import Form from 'react-bootstrap/Form';
   import { useTranslation } from 'react-i18next';
   ```
1. **AA Belt Radar (`@/`)**:
   ```typescript
   import { queryKeys } from '@/Api/query';
   import { formatDate } from '@/Components/Helpers/functions';
   import { SnapshotButtons, SnapshotSelect } from '@/Components/Tables/Snapshot';
   ```
1. **Styles & CSS**:
   ```typescript
   import styles from '@/Components/Tables/BaseTable.module.css';
   ```

## 4. TypeScript & Prop Interfaces

- Export explicit TypeScript prop interfaces for components (`export interface ...Props`).
- Provide sensible defaults for optional arrays or identifiers (`snapshots = []`, etc.).

## 5. Page & Component Architecture (`Pages/` vs `Components/<PageName>/`)

- **Pages (`src/Pages/`) should only act as orchestrators**:
  - Keep page files lean and focused on high-level concerns: routing, top-level queries/mutations, auth/permission checks, and layout composition.
  - Do **not** embed massive forms, long tables, or complex UI blocks directly inside page files.
- **Page-specific Components (`src/Components/<PageName>/`)**:
  - Components that belong to a specific page must be placed in `src/Components/<PageName>/` (e.g. `src/Components/RouteAdmin/RouteCard.tsx`, `src/Components/RouteAdmin/RouteAdminHeader.tsx`).
  - If a feature has further sub-components, group them into subfolders (e.g. `src/Components/Freight/Calculator/`).
  - Provide an `index.ts` file in each component directory that re-exports components using `@/` path aliases.
  - Add clear code comments and hints to components so other developers can easily navigate and edit them.

## 6. Modals Architecture (`Modals/` vs `Components/<PageName>/Modals/`)

- **Only Generic / Base Modals in `src/Components/Modals/`**:
  - The `src/Components/Modals/` folder is reserved **strictly for generic, reusable base modals** (specifically `src/Components/Modals/BaseModal/` and `src/Components/Modals/FenrirModal/`).
  - Do **not** place page-specific modals in `src/Components/Modals/`.
  - All modals must be built using `react-bootstrap`'s `Modal` component (via `FenrirModal`, which wraps `react-bootstrap`'s `Modal` with custom dark/cyan Fenrir styling in `FenrirModal.module.css`).
- **Page-specific Modals (`src/Components/<PageName>/Modals/`)**:
  - All page- or feature-specific modals must reside inside their respective page component directory:
    - `src/Components/RouteAdmin/Modals/` (e.g. `CreateRouteModal.tsx`, `DeleteRouteModal.tsx`)
    - `src/Components/Calculator/Modals/` (e.g. `ContractModal.tsx`, `ConfigurePresetsModal.tsx`)
    - `src/Components/Queue/Modals/` (e.g. `QueueStatusModal.tsx`)
  - Each `Modals/` folder must include an `index.ts` re-exporting its modals using `@/` path aliases.
  - Export explicit TypeScript prop interfaces for every modal (e.g. `isOpen`, `onClose`, `onSubmit`, `isPending`).
  - Provide clear hints and comments so other developers understand the purpose and usage.
- **No Submit via Enter Key in Modals (Button-Only Submission)**:
  - In all modals and forms, submission must **only** be triggered explicitly by clicking a button.
  - Never allow implicit form submission via the Enter key in input fields.
  - Forms inside modals must be defined with `<form onSubmit={(e) => e.preventDefault()}>` and action buttons must use `<Button type="button" onClick={handleSave}>` instead of `type="submit"`.

## 7. React-Bootstrap Components Usage (`Button`, `Tooltip`, `Modal`, `Form`, etc.)

- **Always use `react-bootstrap` components wherever applicable** instead of raw HTML elements or ad-hoc wrappers:
  - **Modals**: Always use `FenrirModal` (which wraps `react-bootstrap`'s `Modal` with `FenrirModal.module.css`). Never create custom fixed-overlay `div` modals from scratch.
  - **Buttons**: Use `react-bootstrap`'s `Button` (`variant="primary"`, `variant="outline-info"`, `variant="danger"`, etc.) with appropriate size and variant props.
  - **Tooltips & Popovers**: Use `react-bootstrap`'s `Tooltip` and `OverlayTrigger` instead of custom tooltip divs or title attributes.
  - **Forms**: Use `react-bootstrap`'s `Form`, `Form.Control`, `Form.Select`, `Form.Check`, etc.
  - **Alerts & Badges**: Use `react-bootstrap`'s `Alert`, `Badge`, etc.
- When custom styling or theme adaptation (dark/cyan EVE theme) is needed, apply CSS modules (e.g. `*.module.css`) or Tailwind utilities alongside the `react-bootstrap` component (e.g., via `className`).

## 8. Internationalization (i18n) & Translation Guidelines

All internationalization (i18n) applies strictly to the React frontend (`frontend/`). Strictly adhere to the following rules:

### A. Golden Rule: Immediate German Translation for Every `t()`

- **Never leave newly added `t(...)` keys untranslated in `frontend/i18n/de/translation.json`**:
  - Whenever you add, modify, or encounter a user-facing string wrapped in `t('...')` in the React frontend (`frontend/src/`), you **MUST** immediately provide and insert the German translation into `frontend/i18n/de/translation.json`.
  - Do **not** leave English placeholder values for new keys in `de/translation.json`.

### B. Standard Translation Workflow

Whenever new UI strings or `t('...')` calls are introduced:

1. **Scan and Extract with `make react-translations`**:

   - Run:
     ```bash
     make react-translations
     ```
   - This executes `i18next-scanner` (via `npm run buildTranslations` in `frontend/`), which parses all `t(...)` calls across `src/**/*.{js,jsx,ts,tsx}` and adds missing keys across all locale files in `frontend/i18n/`.

1. **Translate into German (`frontend/i18n/de/translation.json`)**:

   - Immediately inspect the newly added keys in `frontend/i18n/de/translation.json`.
   - Replace the default English values with accurate, idiomatic German translations tailored to EVE Online and Alliance Auth terminology:
     - **EVE Online Terminology Conventions**:
       - *Courier*: Kurier / Kuriervertrag
       - *Collateral*: Sicherheit / Pfand
       - *Reward*: Belohnung
       - *Solar System*: Sonnensystem
       - *Light-Year (LY)*: Lichtjahr (LJ / LY)
       - *Corridor / Preset*: Korridor / Routen-Vorlage
       - *Queue*: Warteschlange
       - *Stargate Transit*: Stargate-Sprünge / Transit
       - *Jump Drive Distance*: Jump-Drive-Distanz / Sprungdistanz
       - *Status (Pending, In Progress, Finished, Failed)*: Ausstehend, In Bearbeitung, Abgeschlossen, Fehlgeschlagen

1. **Sync English Locale (`frontend/i18n/en/translation.json`)**:

   - Ensure that `frontend/i18n/en/translation.json` contains the exact same keys with proper English values.

1. **Synchronize & Deploy Assets**:

   - Copy translations to Django static directory:
     ```bash
     make react-copy-translations
     ```
   - Or run full build and asset copy:
     ```bash
     make react-test-build
     ```

### C. Writing Translatable Strings in React (`frontend/src/`)

- **Always Wrap User-Facing Text**:

  - Never hardcode raw user-visible text in JSX/TSX without `t(...)`.
  - Import `useTranslation` from `react-i18next`:
    ```typescript
    import { useTranslation } from 'react-i18next';

    export function MyComponent() {
      const { t } = useTranslation();
      return <div>{t('My translatable text')}</div>;
    }
    ```

- **Use Interpolation Instead of String Concatenation**:

  - ❌ **Incorrect**:
    ```typescript
    <span>{t('Showing') + ' ' + start + ' ' + t('to') + ' ' + end}</span>
    ```
  - ✅ **Correct**:
    ```typescript
    <span>
      {t('Showing {{start}}-{{end}} of {{total}} contracts', {
        start,
        end,
        total,
      })}
    </span>
    ```

- **Pluralization**:

  - For counts, use `count` in the interpolation object and support `_one` and `_other` in translation files:
    ```typescript
    t('{{count}} Rows', { count: totalRows });
    ```
    In `de/translation.json`:
    ```json
    "{{count}} Rows_one": "{{count}} Zeile",
    "{{count}} Rows_other": "{{count}} Zeilen"
    ```

## 9. Build, Deployment & Server Restart Rules

- **Always run `make react-test-build` after updating frontend code/data**:
  - Whenever you update React frontend code, components, or translations, run:
    ```bash
    make react-test-build
    ```
  - This command automatically executes `react-build`, `react-copy-assets`, `react-copy-translations`, and `collectstatic`.
  - It deploys the updated static files to the test server and catches any build or type errors immediately so the user can verify changes quickly.
- **Server Restarts Only for `.py` Changes (Always Ask First)**:
  - A server restart is **only** required when Python backend files (`.py`) are modified.
  - **NEVER restart the server automatically**: Always ask the user for permission first before executing any restart.
  - When approved, always use `make restart-test-server` (never raw supervisorctl).
