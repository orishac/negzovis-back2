# Dataset folder structure:
# [dataset_name]:
#     Entities.csv
#     [dataset_name].csv
#     VMap.csv
#     [discretization_id_1]:
#         states.csv
#         KL.txt
#         {or}
#         KL-class-0.0.txt
#         KL-class-1.0.txt
#         [karmalego_id_1]:
#             KL.txt
#             {or}
#             KL-class-0.0.txt
#             KL-class-1.0.txt
#         [karmalego_id_2]:
#         ...
#     [discretization_id_2]:
#     ...
#     visualizations:
#         [visualization_id_1]
#             chunks:
#             chunks_with_entities:
#             search_index_class0
#             search_index_class1
#             entities.json
#             settings.json
#             states.json
#         [visualization_id_2]
#         ...
#

import os
from flask import current_app

from karmalegoweb.src.manage_data.manage_files import path_exists, create_directory

RAW_STATES_FILE_NAME = "states.csv"
JSON_STATES_FILE_NAME = "states.json"
RAW_ENTITIES_FILE_NAME = "entities.csv"
JSON_ENTITIES_FILE_NAME = "entities.json"
KARMALEGO_DIR_NAME = "KL"
KARMALEGO_DIR_NAME_CLASS0 = "KL-class-0.0"
KARMALEGO_DIR_NAME_CLASS1 = "KL-class-1.0"
PARAMS_FILE_NAME = "params"
SETTINGS_FILE_NAME = "settings.json"
CHUNKS_FOLDER_NAME = "chunks"
CHUNKS_ENTITIES_FOLDER_NAME = "chunks_with_entities"
ROOT_FILE_NAME = "root.json"
VISUALIZATION_DIR_NAME = "visualizations"


def __dataset_join(*path):
    return os.path.join(current_app.config["DATASETS_ROOT"], *path)


def dataset_path_exists(*path):
    return path_exists(current_app.config["DATASETS_ROOT"], *path)


def get_settings_path(dataset_name, visualization_id):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)
    return os.path.join(visualization_path, SETTINGS_FILE_NAME)


def get_raw_data_path(dataset_name):
    return __dataset_join(dataset_name, f"{dataset_name}.csv")


def get_raw_states_path(dataset_name, discretization_id):
    return __dataset_join(dataset_name, discretization_id, RAW_STATES_FILE_NAME)


def get_json_states_path(dataset_name, visualization_id):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)
    return os.path.join(visualization_path, JSON_STATES_FILE_NAME)


def get_raw_entities_path(dataset_name):
    return __dataset_join(dataset_name, RAW_ENTITIES_FILE_NAME)


def get_json_entities_path(dataset_name, visualization_id):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)
    return os.path.join(visualization_path, JSON_ENTITIES_FILE_NAME)


def raw_states_exists(dataset_name, discretization_id):
    return dataset_path_exists(get_raw_states_path(dataset_name, discretization_id))


def raw_entities_exists(dataset_name):
    return dataset_path_exists(get_raw_entities_path(dataset_name))


def kl_input_exists(dataset_name, discretization_id, karmalego_id, cls=None):
    return dataset_path_exists(get_kl_path(dataset_name, discretization_id, karmalego_id, cls))


def get_kl_path(dataset_name, discretization_id, karmalego_id, cls=None):
    return __dataset_join(
        dataset_name,
        discretization_id,
        karmalego_id,
        KARMALEGO_DIR_NAME
        if cls is None
        else KARMALEGO_DIR_NAME_CLASS0
        if cls == 0
        else KARMALEGO_DIR_NAME_CLASS1,
    )


def get_kl_params_path(dataset_name, discretization_id, karmalego_id, cls=None):
    kl_path = get_kl_path(dataset_name, discretization_id, karmalego_id, cls)
    return os.path.join(kl_path, PARAMS_FILE_NAME)


def get_tirp_path(dataset_name, discretization_id, karmalego_id, tirp, cls=None):
    kl_path = get_kl_path(dataset_name, discretization_id, karmalego_id, cls)
    return os.path.join(kl_path, tirp)


def get_chunk_path(dataset_name, visualization_id, tirp):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)
    return os.path.join(visualization_path, CHUNKS_FOLDER_NAME, tirp + ".json")


def get_chunk_entities_path(dataset_name, visualization_id, tirp):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)
    return os.path.join(visualization_path, CHUNKS_ENTITIES_FOLDER_NAME, tirp + ".json")


def get_root_path(dataset_name, visualization_id):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)
    return os.path.join(visualization_path, CHUNKS_FOLDER_NAME, ROOT_FILE_NAME)


def get_root_entities_path(dataset_name, visualization_id):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)
    return os.path.join(
        visualization_path,
        CHUNKS_ENTITIES_FOLDER_NAME,
        ROOT_FILE_NAME,
    )


def get_visualization_dir_path(dataset_name, visualization_id):
    return __dataset_join(dataset_name, VISUALIZATION_DIR_NAME, visualization_id)


def create_visualization_folder(dataset_name, visualization_id):
    visualization_path = get_visualization_dir_path(dataset_name, visualization_id)

    paths = [
        visualization_path,
        os.path.join(visualization_path, CHUNKS_ENTITIES_FOLDER_NAME),
        os.path.join(visualization_path, CHUNKS_FOLDER_NAME),
    ]
    for path in paths:
        create_directory(path)
