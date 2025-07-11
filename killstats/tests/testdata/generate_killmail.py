# AA Killstats
from killstats.models.killboard import Attacker, Killmail


def create_killmail(**kwargs) -> Killmail:
    """Create a Killmail"""
    params = {}
    params.update(kwargs)

    killmail = Killmail(**params)
    killmail.save()
    return killmail


def create_attacker(**kwargs) -> Attacker:
    """Create an Attacker"""
    params = {}
    params.update(kwargs)

    attacker = Attacker(**params)
    attacker.save()
    return attacker
