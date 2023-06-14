from flask import current_app

from karmalegoweb.src import models

from karmalegoweb.src.manage_data.translate_data import (
    karmalego_to_dataset_name,
    karmalego_to_discretization,
)
from karmalegoweb.src.manage_data.__directory_structure import (
    dataset_path_exists,
    get_raw_data_path,
    raw_entities_exists,
    raw_states_exists as raw_states_data_exists,
    kl_input_exists,
)
from karmalegoweb.src.manage_data.manage_files import read_csv


def raw_states_exists(discretization_id):
    discretization = models.discretization.query.filter_by(id=discretization_id).first()
    if not discretization:
        current_app.logger.warning(f"Could not find given discretization id: {discretization_id}")
        return False
    return raw_states_data_exists(discretization.dataset_Name, discretization_id)


def has_entities(dataset_name):
    return raw_entities_exists(dataset_name)


def karmalego_data_exists(karmalego_id):
    discretization_id = karmalego_to_discretization(karmalego_id)
    if discretization_id is None:
        return False
    discretization = models.discretization.query.filter_by(id=discretization_id).first()
    if not discretization:
        current_app.logger.error(
            f"Could not find the discretization {discretization} of the data mining {karmalego_id} in the database"
        )
        return False

    dataset_name = karmalego_to_dataset_name(karmalego_id)

    def kl_exists(cls=None):
        return kl_input_exists(
            dataset_name,
            discretization_id,
            karmalego_id,
            cls,
        )

    two_class = is_two_class(dataset_name)
    if two_class:
        return kl_exists(0) and kl_exists(1)
    else:
        return kl_exists()


def is_two_class(dataset_name):
    path = get_raw_data_path(dataset_name)
    if not dataset_path_exists(path):
        return None
    raw_data = read_csv(path)
    return len(raw_data[raw_data["TemporalPropertyID"] == -1]) > 0
