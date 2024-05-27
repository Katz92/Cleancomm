"""
Enumerations for Assignment's option field.
"""
from enum import Enum


class Options(Enum):
    """
    Enumeration class for option field
    """
    ABSENCE_DELEGATION = "absenceAndDelegation"
    ABSENCE = "absence"
    DELEGATION = "delegation"
