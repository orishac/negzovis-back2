import uuid

from flask import current_app

from karmalegoweb.src.db import get_db
from karmalegoweb.src import models
from karmalegoweb.src.manage_data.__directory_structure import (
    get_settings_path,
    get_raw_entities_path,
    get_json_entities_path,
    get_raw_states_path,
    get_json_states_path,
    get_chunk_path,
    get_chunk_entities_path,
    get_root_entities_path,
    get_root_path,
    create_visualization_folder,
)
from karmalegoweb.src.manage_data.manage_files import (
    dict_to_json_file,
    csv_to_arr,
    arr_to_json_file,
)


def create_empty_visualization(karmalego_id, dataset_name):
    run_id = str(uuid.uuid4())
    new_run = models.run(id=run_id)

    visualization_id = str(uuid.uuid4())
    new_visualization = models.Visualization(
        id=visualization_id, KL_id=karmalego_id, dataset=dataset_name, run=new_run.id
    )
    db = get_db()
    db.session.add(new_visualization)
    db.session.add(new_run)
    create_visualization_folder(dataset_name, visualization_id)
    db.session.commit()

    return new_visualization


def finish_preproccess_run(visualization_id, success, message=""):
    visualization = models.Visualization.query.filter_by(id=visualization_id).first()
    run_id = visualization.run
    run = models.run.query.filter_by(id=run_id).first()
    run.finished = True
    run.success = success
    run.message = message

    db = get_db()
    db.session.commit()


def create_settings(dataset_name, visualization_id, settings: dict):
    path = get_settings_path(dataset_name, visualization_id)
    dict_to_json_file(path, settings)


def create_entities(dataset_name, visualization_id):
    old_path = get_raw_entities_path(dataset_name)
    new_path = get_json_entities_path(dataset_name, visualization_id)
    entities = csv_to_arr(old_path)
    arr_to_json_file(new_path, entities)
    return entities


def create_states(dataset_name, discretization_id, visualization_id):
    old_path = get_raw_states_path(dataset_name, discretization_id)
    new_path = get_json_states_path(dataset_name, visualization_id)
    states = csv_to_arr(old_path)
    arr_to_json_file(new_path, states)
    return states


def save_tirps_entities(datasetname, visualization_id, tirps: list):
    for tirp in tirps:
        if tirp.size != 1:
            current_app.logger.error(f"Was requested to save a tirp with size: {tirp.size}")
        path = get_chunk_entities_path(datasetname, visualization_id, tirp.symbols[0])
        dict_to_json_file(path, tirp.__dict__)


def save_tirps_no_entities(datasetname, visualization_id, tirps: list):
    for tirp in tirps:
        if tirp.size != 1:
            current_app.logger.error(f"Was requested to save a tirp with size: {tirp.size}")
        path = get_chunk_path(datasetname, visualization_id, tirp.symbols[0])
        dict_to_json_file(path, tirp.__dict__)


def save_root_entities(datasetname, visualization_id, root: list):
    path = get_root_entities_path(datasetname, visualization_id)
    dict_to_json_file(path, root)


def save_root_no_entities(datasetname, visualization_id, root: list):
    path = get_root_path(datasetname, visualization_id)
    dict_to_json_file(path, root)
