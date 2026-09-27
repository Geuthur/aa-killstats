# Alliance Auth Testing Guidelines (aa-test-guidelines)

This document defines mandatory testing standards and conventions for Alliance Auth packages and plugins in this workspace.

______________________________________________________________________

## 1. Mandatory Base Test Case: `AuthTestCase`

**Never use Django's default `TestCase` (`from django.test import TestCase`) directly in tests.**
Always inherit from **`AuthTestCase`** (e.g. `from killstats.tests import AuthTestCase`).

### A. Rationale & Benefits

1. **Network Guard (`NoSocketsTestCase`)**:
   `AuthTestCase` inherits from `NoSocketsTestCase`, which monkey-patches sockets during test execution. This strictly prevents accidental live network calls (e.g. to ESI or external APIs), ensuring tests remain fast, offline-capable, and hermetic.
1. **Pre-configured Authentication Objects**:
   - `self.factory`: Django `RequestFactory` for view requests.
   - `self.user`: Pre-configured standard user with default application permissions via `UserMainFactory`.
   - `self.superuser`: Pre-configured user with `is_superuser = True`.
1. **Middleware Helper**:
   - `self._middleware_process_request(request)`: Helper to attach session and message middleware to mocked requests.

```python
# GOOD:
from killstats.tests import AuthTestCase


class MyViewTest(AuthTestCase): ...


# BAD:
from django.test import TestCase


class MyViewTest(TestCase): ...
```

______________________________________________________________________

## 2. Test Isolation & Custom User/Character Setup

Do not mutate shared character state on `self.user` across tests. Instead, when a test requires specific character data (such as an NPC corporation, missing alliance, or specific permissions), instantiate a fresh user using `UserMainFactory` with `main_character__character`:

```python
user = UserMainFactory(
    main_character__character=EveCharacterFactory(
        corporation=EveCorporationFactory(),
    )
)
```

### Corporation & Automatic Alliance Creation via `EveCorporationFactory`:

Always use **`EveCorporationFactory`** (from `evesde_factory.allianceauth`) to define corporation attributes. `EveCorporationFactory` automatically creates the associated `alliance` (with `executor_corp_id` set to the corporation ID), and `EveCharacterFactory` automatically inherits `alliance_id`, `alliance_name`, and `alliance_ticker` from `corporation.alliance`.

- **Standard Corporation (Alliance auto-generated)**:
  ```python
  EveCharacterFactory(
      corporation=EveCorporationFactory(),
  )
  ```
- **Custom Corporation Attributes & Auto-Alliance**:
  ```python
  EveCharacterFactory(
      corporation=EveCorporationFactory(
          corporation_id=98000001,
          corporation_name="Player Corp",
      ),
  )
  ```
- **NPC Corporation without Alliance**:
  ```python
  EveCharacterFactory(
      corporation=EveCorporationFactory(
          corporation_id=1000125,  # NPC Corp
          create_alliance=False,  # Do not create alliance
      ),
  )
  ```
- **Corporation with Specific Alliance (`EveAllianceInfoFactory`)**:
  ```python
  EveCharacterFactory(
      corporation=EveCorporationFactory(
          alliance=EveAllianceInfoFactory(
              alliance_id=99000001,
              alliance_name="Specific Alliance",
          ),
      ),
  )
  ```
- **Custom Permissions**:
  Pass permissions directly to `UserMainFactory`: `permissions__=["killstats.admin_access"]`.

### Example:

```python
def test_add_alliance_npc_corporation_rejected(self, mock_messages):
    # Test Data
    user = UserMainFactory(
        permissions__=["killstats.admin_access"],
        main_character__character=EveCharacterFactory(
            corporation=EveCorporationFactory(
                corporation_id=1000125,  # NPC Corporation
                create_alliance=False,
            ),
        ),
    )
    token = user.token_set.first()

    # Test Action
    response = self._add_alliance(user, token)

    # Expected Result
    self.assertEqual(response.status_code, HTTPStatus.FOUND)
    self.assertEqual(response.url, reverse("killstats:index"))
    self.assertEqual(mock_messages.error.call_count, 1)
```

______________________________________________________________________

## 3. Mandatory Use of Factories for Test Data

**Never create test data manually via direct ORM calls (e.g. `Model.objects.create(...)`) when a factory exists.**
Always use the corresponding **Factory Boy** factories to create characters, corporations, alliances, and app-specific models.

### A. Factory Sources & Locations

1. **Alliance Auth & EVE SDE Models** -> **`evesde_factory`**:

   - Characters: `from evesde_factory.allianceauth import EveCharacterFactory`
   - Corporations: `from evesde_factory.allianceauth import EveCorporationFactory, EveCorporationInfoFactory`
   - Alliances: `from evesde_factory.allianceauth import EveAllianceFactory, EveAllianceInfoFactory`
   - Users: `from evesde_factory.allianceauth import UserFactory`
   - SDE Models: `from evesde_factory.eve_sde import ItemTypeFactory, SolarSystemFactory`

1. **App-Specific Models** -> **`<app>.tests.testdata`**:

   - All plugin- or app-specific model factories reside in `tests/testdata/` within that app.
   - Example (`killstats`):
     ```python
     from killstats.tests.testdata.killstats import (
         AlliancesAuditFactory,
         AttackerFactory,
         CorporationsAuditFactory,
         EveEntityFactory,
         KillmailFactory,
         UserMainFactory,
     )
     ```

### B. Best Practices & Automatic Data Generation

- **Parameterless Invocation (Default)**:
  Factories generate all required fields and relations automatically (using sequences, fakers, and subfactories). Therefore, **always call factories without arguments by default**. Only pass explicit attributes if the specific test case requires particular IDs, names, or relationships:

  ```python
  # GOOD - Let the factory generate valid default test data automatically:
  corp = EveCorporationInfoFactory()
  char = EveCharacterFactory()
  killmail = KillmailFactory()

  # GOOD - Explicit attributes only when strictly required by the test case:
  npc_corp = EveCorporationInfoFactory(
      corporation_id=1000125
  )  # Specific NPC ID needed for test
  char_with_corp = EveCharacterFactory(corporation=corp)  # Specific relationship needed

  # BAD - Unnecessary boilerplate overrides for fields the test doesn't care about:
  corp = EveCorporationInfoFactory(
      corporation_id=98000001,
      corporation_name="Player Corp",
      corporation_ticker="PC",
      member_count=50,
  )
  ```

- **Avoid Direct ORM Calls**:

  ```python
  # BAD:
  corp = EveCorporationInfo.objects.create(corporation_id=98000001, ...)
  char = EveCharacter.objects.create(...)
  killmail = Killmail.objects.create(...)
  ```

- Factories automatically handle foreign keys, dependencies, sequences, related objects, and sane default values, preventing database integrity errors and unnecessary boilerplate in test files.

______________________________________________________________________

## 4. Test Method Structure (Arrange - Act - Assert)

Every test method MUST be clearly partitioned into three distinct sections marked with explicit comments:

1. `# Test Data` (Arrange): Set up factories, models, tokens, and mock return values.
1. `# Test Action` (Act): Execute the function, view, task, or command under test.
1. `# Expected Result` (Assert): Verify return values, HTTP response status codes, redirects, database state, and mock assertions.

### Reference Layout:

```python
def test_add_alliance_should_succeed(self, mock_messages):
    # Test Data
    token = self.user.token_set.first()
    char = self.user.profile.main_character
    alliance, _ = EveAllianceInfo.objects.get_or_create(
        alliance_id=char.alliance_id,
        defaults={
            "alliance_name": char.alliance_name,
            "alliance_ticker": char.alliance_ticker,
            "executor_corp_id": char.corporation_id,
        },
    )

    # Test Action
    response = self._add_alliance(self.user, token)

    # Expected Result
    alliance_audit = AlliancesAudit.objects.get(alliance=alliance)
    self.assertEqual(response.status_code, HTTPStatus.FOUND)
    self.assertEqual(
        response.url, reverse("killstats:alliance", args=[char.alliance_id])
    )
    self.assertEqual(mock_messages.info.call_count, 1)
    self.assertEqual(alliance_audit.alliance.alliance_id, char.alliance_id)
```

______________________________________________________________________

## 5. Naming & Mocking Conventions

### A. Method Naming

- Pattern: `test_<method_name>_should_<expected_behavior>` or `test_<action>_<expected_outcome>`.
- Examples:
  - `test_should_return_none_on_invalid_data`
  - `test_add_corp_should_reject_npc_corporation`

### B. Patching & Mocking

- Define `MODULE_PATH = "<full.import.path>"` near the top of the test module.
- Use `@patch(f"{MODULE_PATH}.<target>")` decorators.
- **Never mock manager methods (such as `objects.get_or_create`)** if factories rely on them or if the code under test uses real database lookups.
