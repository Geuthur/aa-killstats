# Testing Guidelines for Backend

When developing and verifying features, refactorings, or bugfixes in this repository, strictly adhere to the following test workflows:

## 1. Backend Python Tests

Always use `make coverage` in the Respetory Directory to test and verify the Python backend code.

- **Command**: `make coverage`
- **Purpose**: Runs the complete test suite against Django / Alliance Auth with coverage tracking and generates coverage reports (`coverage.xml` / `htmlcov/index.html`).
- **Prerequisite**: Ensure the Python virtual environment is active before running (or run in an environment where `/home/testauth/venv/bin/activate` is sourced).

```bash
make coverage
```

## 2. Frontend React Tests

Always use `make react-test` or `npm test` inside `frontend/` to test React code.

- **Command**: `make react-test` (or `cd frontend && npm test`)
- **Linter**: `make react-lint` (or `cd frontend && npm run lint`)
- **Build Verification**: `make react-build` (or `cd frontend && npm run build`)

## 3. Python Backend Test Method Structure & Layout

When writing unit tests for Python backend code, strictly adhere to the following conventions:

### A. Naming Convention

- Method names must follow the pattern: `test_<method_name>_should_<expected_behavior>` (or `test_should_<expected_behavior>` if testing a single-purpose test class).
- Examples:
  - `test_get_character_portrait_url_should_return_url`
  - `test_get_character_portrait_url_should_return_empty_for_invalid_input`

### B. Patching & Mocking Convention

- Define `MODULE_PATH = "<full.import.path>"` at module level near the top of the test file.
- Use `@patch(f"{MODULE_PATH}.<target_function>")` decorators.
- Name mock arguments to match the patched target: `mock_<target_function>`.
- Always verify that mocks were called with the expected arguments: `mock_<target_function>.assert_called_once_with(...)`.

### C. Structure (Arrange - Act - Assert)

Every test method MUST contain exactly three clear sections marked with explicit comments:

1. `# Test Data` (Arrange): Define mock return values, inputs, parameters, and test models.
1. `# Test Action` (Act): Call the method/function under test and capture the return value or exception.
1. `# Expected Result` (Assert): Assert outputs, database changes, and mock call assertions.

### D. Reference Layout

```python
@patch(f"{MODULE_PATH}.character_portrait_url")
def test_get_character_portrait_url_should_return_url(
    self, mock_character_portrait_url
):
    # Test Data
    mock_character_portrait_url.return_value = "https://images.example/characters/1001"

    # Test Action
    result = eveonline.get_character_portrait_url(character_id=1001, size=64)

    # Expected Result
    self.assertEqual(result, "https://images.example/characters/1001")
    mock_character_portrait_url.assert_called_once_with(character_id=1001, size=64)
```
