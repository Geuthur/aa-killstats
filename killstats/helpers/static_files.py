"""
Helper functions for static integrity calculations
"""

import logging

# Standard Library
import os
from pathlib import Path

# Third Party
from sri import Algorithm, calculate_integrity

# AA Fleet Pings
from killstats import __title__
from killstats.constants import AA_KILLSTATS_STATIC_DIR

logger = logging.getLogger(__name__)


def calculate_integrity_hash(relative_file_path: str) -> str:
    """
    Calculates the integrity hash for a given static file
    :param self:
    :type self:
    :param relative_file_path: The file path relative to the `aa-killstats/killstats/static/killstats` folder
    :type relative_file_path: str
    :return: The integrity hash
    :rtype: str
    """

    file_path = os.path.join(AA_KILLSTATS_STATIC_DIR, relative_file_path)
    integrity_hash = calculate_integrity(Path(file_path), Algorithm.SHA512)

    return integrity_hash
