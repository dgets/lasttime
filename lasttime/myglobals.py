from enum import Enum


class Dosage(Enum):
    """
    Different dosage units
    """
    mcg = 1
    mg = 2
    ml = 3
    tsp = 4
    floz = 5


class TimeSpan(Enum):
    """
    Different time span variants
    """
    min = 1
    hr = 2
    day = 3