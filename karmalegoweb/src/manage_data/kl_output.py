from karmalegoweb.src.manage_data.translate_data import (
    karmalego_to_dataset_name,
    karmalego_to_discretization,
)
from karmalegoweb.src.manage_data.__directory_structure import (
    get_kl_params_path,
    get_kl_path,
    get_tirp_path,
)

from karmalegoweb.src.manage_data.manage_files import read_first_line, get_files_in_directory


def get_params(kl_id, cls=None):
    discretization_id = karmalego_to_discretization(kl_id)
    dataset_name = karmalego_to_dataset_name(kl_id)
    path = get_kl_params_path(dataset_name, discretization_id, kl_id, cls)
    return read_first_line(path)


def get_tirps_names(kl_id, cls=None):
    dataset_name = karmalego_to_dataset_name(kl_id)
    discretization_id = karmalego_to_discretization(kl_id)
    dir_path = get_kl_path(dataset_name, discretization_id, kl_id, cls)
    all_files = get_files_in_directory(dir_path)
    return [file_name for file_name in all_files if file_name.endswith(".tirp")]


def read_tirp(kl_id, tirp_name, cls=None):
    dataset_name = karmalego_to_dataset_name(kl_id)
    discretization_id = karmalego_to_discretization(kl_id)
    tirp_path = get_tirp_path(dataset_name, discretization_id, kl_id, cls, tirp_name)
    with open(tirp_path, "r") as file:
        tirps_params_line = file.readline()
        data_lines = file.readlines()
        return tirps_params_line, data_lines
