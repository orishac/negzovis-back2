import os
import shutil

from flask import current_app

from karmalegoweb.src.manage_data.manage_files import (
    arr_to_json_file,
    csv_to_arr,
    set_json_property,
)
from karmalegoweb.src.upload_manager import validate_entities as is_valid_entities
from karmalegoweb.src.manage_data.__directory_structure import (
    get_raw_data_path,
    get_raw_entities_path,
    get_json_entities_path,
    get_settings_path,
)
from karmalegoweb.src import models


def validate_entities(dataset_name, entities_uuid):
    raw_data_path = get_raw_data_path(dataset_name)
    return is_valid_entities(raw_data_path, entities_uuid)


def upload_entities_to_dataset(dataset_name, entities_uuid):
    src_path = os.path.join(current_app.config["TEMP_PATH"], entities_uuid)
    dest_path = get_raw_entities_path(dataset_name)
    shutil.copy(src_path, dest_path)

    entities = csv_to_arr(dest_path)

    visualizations = models.Visualization.query.filter_by(dataset=dataset_name).all()
    for visualization in visualizations:
        entities_json_path = get_json_entities_path(dataset_name, visualization.id)
        settings_path = get_settings_path(dataset_name, visualization.id)

        arr_to_json_file(entities_json_path, entities)
        set_json_property(settings_path, "has_entities", True)
