# Alliance Auth (AA) Development Guidelines

This document outlines the mandatory development standards and conventions for Alliance Auth packages and plugins in this workspace.

______________________________________________________________________

## 1. Mandatory Test Factories for Every Model

Whenever a new model or schema is created or modified, **a corresponding Factory MUST always be created or updated**. Hand-crafted dictionaries or mock objects must not replace structured factories in unit tests.

### A. Scope of Requirement

- **All Django Database Models**: Every model in `<app_name>/models/` MUST have a corresponding `DjangoModelFactory`.
- **All Pydantic Schemas / DTOs**: Every Pydantic model, ESI schema, or API response model in `<app_name>/helpers/` or `<app_name>/schema/` MUST have a corresponding `BasePydanticFactory`.
- **Storage Location**: All factories must be located in `<app_name>/tests/testdata/<app_name>.py`.

______________________________________________________________________

## 2. Factory Architecture & Type Hints

All factories must follow the conventions established in `aa-beltradar` and `aa-evesde-factory`.

### A. Metaclass & Typing (`BaseMetaFactory`)

Every factory MUST use `metaclass=BaseMetaFactory[ModelClass]` from `evesde_factory.allianceauth.BaseMetaFactory`:

- This guarantees full IDE auto-completion and static type checking when instantiating factories (`instance = MyModelFactory()`).
- The return type is always explicitly recognized as the model class, not `Any` or factory internals.

### B. Django Model Factories

- Inherit from `BaseDjangoModelFactory` (or `factory.django.DjangoModelFactory`).
- Always define `class Meta: model = ModelClass` and `django_get_or_create = (...)` for unique fields.
- Leverage `evesde_factory` for related Alliance Auth and EVE SDE models:
  - `EveCharacterFactory`, `EveCorporationInfoFactory`, `EveAllianceInfoFactory`
  - `ItemTypeFactory`, `SolarSystemFactory`
- Provide `to_model(**kwargs)` and `as_model(**kwargs)` methods to explicitly return the generated model instance.

```python
class MyModelFactory(BaseDjangoModelFactory, metaclass=BaseMetaFactory[MyModel]):
    """Generate a MyModel database object with realistic defaults."""

    class Meta:
        model = MyModel
        django_get_or_create = ("id",)

    id = factory.Sequence(lambda n: 1000 + n)
    character = factory.SubFactory(EveCharacterFactory)
```

### C. Pydantic Model Factories

- Inherit from `BasePydanticFactory[ModelClass], metaclass=BaseMetaFactory[ModelClass]`.
- Must provide the following uniform methods:
  - `.to_model(**kwargs)` / `.as_model(**kwargs)`: Returns the validated Pydantic model instance.
  - `.to_dict(**kwargs)` / `.as_dict(**kwargs)`: Returns a JSON-serializable dictionary (`model_dump(mode="json")`).
  - `.to_json(**kwargs)` / `.as_json(**kwargs)`: Returns a JSON string (`model_dump_json()`).

```python
class MySchemaFactory(
    BasePydanticFactory[MySchema], metaclass=BaseMetaFactory[MySchema]
):
    """Generate a MySchema Pydantic model."""

    class Meta:
        model = MySchema

    field_a = factory.fuzzy.FuzzyInteger(1, 100)
    field_b = factory.SubFactory(NestedSchemaFactory)
```

______________________________________________________________________

## 3. User & Authentication Factories

Every AA app test suite must provide a standard `UserMainFactory`:

- Inherits from `evesde_factory.allianceauth.UserFactory`.
- Sets default app permissions in `permissions__` (e.g. `["myapp.basic_access"]`).
- Automatically creates and attaches a main character using `evesde_factory.utils.add_character_to_user`.

```python
class UserMainFactory(UserFactory):
    """Generate a User object with a main character and default permissions."""

    permissions__ = ["myapp.basic_access"]
    scopes__ = ["publicData"]

    @factory.post_generation
    def main_character(obj, create, _, **kwargs):
        if not create:
            return
        character = kwargs.get("character") or EveCharacterFactory(
            character_name=f"{obj.first_name} {obj.last_name}"
        )
        add_character_to_user(
            user=obj,
            character=character,
            is_main=True,
            scopes=obj._main_character_scopes,
        )
```

______________________________________________________________________

## 4. Usage in Unit Tests

In test cases (`# Test Data` section):

1. **Always use factories** instead of raw model constructors or dictionary literals.
1. For testing API endpoints and mocks:
   - Use `Factory.to_dict()` or `model.as_dict()` when setting mock JSON payloads (`response.json.return_value = model.as_dict()`).
   - Use `Factory.to_json()` when testing raw response payloads.
   - Use `Factory()` or `Factory.to_model()` when comparing validated model instances (`self.assertEqual(result, model)`).
