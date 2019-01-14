from enum import Enum


class Units(Enum):
    """
    Different dosage units
    """
    mcg = 'MCG'
    mg = 'MG'
    ml = 'ML'
    tsp = 'TSP'
    floz = 'FL OZ'


class HalfLifeSpan(Enum):
    """
    Different time span variants
    """
    min = 'MIN'
    hr = 'HR'
    # day = 'DAY'
