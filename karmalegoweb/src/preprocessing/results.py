import enum


class preprocessins_results(enum.Enum):
    GOOD = 0
    MISSING_KARMALEGO = 1
    MISSING_STATES = 2
    VISUALIZATION_EXISTS = 3
    EXCEPTION = 4
