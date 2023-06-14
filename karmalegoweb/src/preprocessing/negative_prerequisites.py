from karmalegoweb.src.preprocessing.results import preprocessins_results
from karmalegoweb.src.manage_data.translate_negative_data import (
    karma_lego_to_visualization,
    karmalego_to_discretization,
)
from karmalegoweb.src.manage_data.negative_data_checks import (
    raw_states_exists,
    karmalego_data_exists,
)

# This module we check every thing we need before starting to process the karmalego output into visualization data


def validate(karmalego_id: str):
    GOOD = preprocessins_results.GOOD
    for validation in VALIDATIONS:
        result = validation(karmalego_id)
        if result != GOOD:
            return result
    return GOOD

def validate_seq(karmalego_id: str):
    GOOD = preprocessins_results.GOOD
    for validation in SEQ_VALIDATIONS:
        result = validation(karmalego_id)
        if result != GOOD:
            return result
    return GOOD


def __input_exists(karmalego_id):
    if not karmalego_data_exists(karmalego_id):
        return preprocessins_results.MISSING_KARMALEGO
    discretization_id = karmalego_to_discretization(karmalego_id)
    if not raw_states_exists(discretization_id):
        return preprocessins_results.MISSING_STATES
    return preprocessins_results.GOOD


def __visualization_not_already_exists(karmalego_id):
    visualization_id = karma_lego_to_visualization(karmalego_id)
    if visualization_id is None:
        return preprocessins_results.GOOD
    return preprocessins_results.VISUALIZATION_EXISTS


VALIDATIONS = [__input_exists, __visualization_not_already_exists]
SEQ_VALIDATIONS = [__visualization_not_already_exists]
