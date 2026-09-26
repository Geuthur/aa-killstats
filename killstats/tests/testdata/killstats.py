# Third Party
import factory
from evesde_factory.allianceauth import (
    EveCharacterFactory,
    UserFactory,
)

# AA Factories
from evesde_factory.utils import add_character_to_user


class UserMainFactory(UserFactory):
    """Generate a User object with a main character and default permissions for Belt Radar."""

    permissions__ = ["killstats.basic_access"]
    scopes__ = ["publicData"]

    @factory.post_generation
    def main_character(obj, create, _, **kwargs):
        if not create:
            return
        if "character" in kwargs:
            character = kwargs["character"]
        else:
            character_name = f"{obj.first_name} {obj.last_name}"
            character = EveCharacterFactory(character_name=character_name)

        add_character_to_user(
            user=obj,
            character=character,
            is_main=True,
            scopes=obj._main_character_scopes,
        )
