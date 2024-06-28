# Standard Library
from typing import Any, Tuple

# Django
from django.db import models

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.eveonline.providers import ObjectNotFound

# AA Killstats
from killstats import providers
from killstats.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class GeneralQuerySet(models.QuerySet):

    def visible_to(self, user):
        # superusers get all visible
        if user.is_superuser:
            logger.debug("Returning all Data for superuser %s.", user)
            return self

        if user.has_perm("killstats.admin_access"):
            logger.debug("Returning all Data for %s.", user)
            return self
        try:
            char = user.profile.main_character
            assert char
            # build all accepted queries
            queries = [models.Q(character__character_ownership__user=user)]

            logger.debug(
                "%s queries for user %s visible chracters.", len(queries), user
            )
            # filter based on queries
            query = queries.pop()
            for q in queries:
                query |= q
            return self.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return self.none()


class GeneralManager(models.Manager):
    def get_queryset(self):
        return GeneralQuerySet(self.model, using=self._db)

    @staticmethod
    def visible_eve_characters(user):
        qs = EveCharacter.objects.get_queryset()
        if user.is_superuser:
            logger.debug("Returning all characters for superuser %s.", user)
            return qs.all()

        if user.has_perm("killstats.admin_access"):
            logger.debug("Returning all characters for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            assert char
            # build all accepted queries
            queries = [models.Q(character_ownership__user=user)]

            logger.debug(
                "%s queries for user %s visible chracters.", len(queries), user
            )
            # filter based on queries
            query = queries.pop()
            for q in queries:
                query |= q
            return qs.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)


class EveEntityManager(models.Manager):
    def get_or_create_esi(self, *, entity_id: int) -> Tuple[Any, bool]:
        """gets or creates entity object with data fetched from ESI"""
        # AA Killstats
        # pylint: disable=import-outside-toplevel
        from killstats.models.general import EveEntity

        try:
            entity = self.get(eve_id=entity_id)
            return entity, False
        except EveEntity.DoesNotExist:
            return self.update_or_create_esi(entity_id=entity_id)

    def create_bulk_from_esi(self, eve_ids):
        """gets bulk names with ESI"""
        if len(eve_ids) > 0:
            # AA Killstats
            # pylint: disable=import-outside-toplevel
            from killstats.models.general import EveEntity

            chunk_size = 500
            id_chunks = [
                eve_ids[i : i + chunk_size] for i in range(0, len(eve_ids), chunk_size)
            ]
            for chunk in id_chunks:
                response = providers.esi.client.Universe.post_universe_names(
                    ids=chunk
                ).results()
                new_names = []
                logger.debug(
                    "Eve Entity Manager EveName: count in %s count out %s",
                    len(chunk),
                    len(response),
                )
                for entity in response:
                    new_names.append(
                        EveEntity(
                            eve_id=entity["id"],
                            name=entity["name"],
                            category=entity["category"],
                        )
                    )
                EveEntity.objects.bulk_create(new_names, ignore_conflicts=True)
            return True
        return True

    def update_or_create_esi(self, *, entity_id: int) -> Tuple[Any, bool]:
        """updates or creates entity object with data fetched from ESI"""
        response = providers.esi.client.Universe.post_universe_names(
            ids=[entity_id]
        ).results()
        if len(response) != 1:
            raise ObjectNotFound(entity_id, "unknown_type")
        entity_data = response[0]
        return self.update_or_create(
            eve_id=entity_data["id"],
            defaults={
                "name": entity_data["name"],
                "category": entity_data["category"],
            },
        )
