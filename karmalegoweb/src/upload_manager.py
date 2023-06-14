import os, uuid, shutil, zipfile

from werkzeug.utils import secure_filename
from flask import current_app, g

from karmalegoweb.src import models
from karmalegoweb.src.db import get_db
from karmalegoweb.src.files_validation import raw_data, entities, vmap


def log_inconsistencies():
    dataset_directory = current_app.config["DATASETS_ROOT"]

    datasets = list(
        filter(
            lambda file: os.path.isdir(os.path.join(dataset_directory, file)),
            os.listdir(dataset_directory),
        )
    )
    for dataset in datasets:
        database_dataset = models.info_about_datasets.query.filter_by(Name=dataset).first()
        if database_dataset is None:
            current_app.logger.warning(
                f"The dataset directory, {dataset}, exists but it is not saved in the database"
            )

    for dataset in models.info_about_datasets.query.all():
        if dataset.Name not in datasets:
            current_app.logger.warning(
                f"The dataset, {dataset}, exists in the databe but a directory for the data could not be found"
            )


def __get_dataset_dir_path(dataset_name):
    return os.path.join(current_app.config["DATASETS_ROOT"], dataset_name)


def __create_directory_for_dataset(dataset_name):
    try:
        dir_path = __get_dataset_dir_path(dataset_name)
        os.makedirs(dir_path)
    except OSError as e:
        current_app.logger.error(f"Creation of the directory {dataset_name} failed:\n{e}")
        raise e


def __delete_directory_for_dataset(dataset_name):
    try:
        dir_path = __get_dataset_dir_path(dataset_name)
        shutil.rmtree(dir_path)
    except OSError as e:
        current_app.logger.error(f"Deletion of {dataset_name}'s files failed:\n{e}")


def __save_metadata(dataset_name, description, dataset_source, public_private, category):
    dataset = models.info_about_datasets(
        Name=dataset_name,
        Description=description,
        source=dataset_source,
        public_private=public_private,
        category=category,
        size=0,
        views=0,
        downloads=0,
        owner=g.user,
        # Ravid: what is this?
        visual_reference="",
        uploaded=True,
    )
    db = get_db()
    db.session.add(dataset)
    db.session.commit()


def __validate_new_dataset(rawDataUuid, vmapUuid, entitiesUuid):
    raw_data_path = os.path.join(current_app.config["TEMP_PATH"], rawDataUuid)
    if not raw_data.validate_data_header(raw_data_path):
        return (
            False,
            f"Either your Dataset's header is not in the correct format,\nor you have more or less than {str(len(current_app.config['RAW_DATA_HEADER_FORMAT']))} columns in your raw data",
        )
    if not raw_data.validate_data_body(raw_data_path):
        return False, "At least one row in your raw data is not in the correct format", 400

    vmap_path = os.path.join(current_app.config["TEMP_PATH"], vmapUuid)
    if not vmap.validate_header(vmap_path):
        return (
            False,
            f"Either your VMap File's header is not in the correct format, or you have more than \n{str(len(current_app.config['VMAP_HEADER_FORMAT']))} columns in your data",
        )

    if not vmap.validate_id_integrity(raw_data_path, vmap_path):
        return (
            False,
            "The list of variables you provided does not match the raw data file.\nPlease make sure you are mapping each and every variable id in your data, and only the ones in your data.",
        )

    if entitiesUuid:
        return validate_entities(raw_data_path, entitiesUuid)

    return True, "Valid Data"


def validate_entities(raw_data_path, entitiesUuid):
    entities_path = os.path.join(current_app.config["TEMP_PATH"], entitiesUuid)

    if not entities.validate_id_column(entities_path):
        return False, 'Left most column of the entities file must be "id"'

    if not entities.validate_id_integrity(raw_data_path, entities_path):
        return (
            False,
            "The list of entities you provided does not match the raw data file.\nPlease make sure you are mapping each and every entity id in your data,\nnd only the ones in your data.",
        )
    return True, "Valid Data"


def __move_files(dataset_name, rawDataUuid, vmapUuid, entitiesUuid):
    to_move = {rawDataUuid: dataset_name, vmapUuid: "VMap"}
    if entitiesUuid:
        to_move[entitiesUuid] = "Entities"

    for file_name in to_move:
        src_path = os.path.join(current_app.config["TEMP_PATH"], file_name)
        dest_path_dir = __get_dataset_dir_path(dataset_name)
        dest_path = os.path.join(dest_path_dir, to_move[file_name] + ".csv")
        shutil.copy(src_path, dest_path)


def __validate_file_existence(uuid, file_name):
    exists = models.data_file.query.filter_by(uuid=uuid).first()
    if exists is None:
        return False, f"Requested {file_name} file does not exist"
    if not exists.uploaded_successfully:
        return False, f"Requested {file_name} file has not been fully uploaded"
    return True, "File uploaded successfully"


def upload_new_dataset(
    dataset_name,
    description,
    dataset_source,
    public_private,
    category,
    rawDataUuid,
    vmapUuid,
    entitiesUuid,
) -> tuple:
    dataset_name = secure_filename(dataset_name)
    if dataset_name == "":
        return False, "Invalid dataset name"

    for uuid, file_name in [
        (rawDataUuid, "raw data"),
        (vmapUuid, "vmap"),
        (entitiesUuid, "entities"),
    ]:
        if uuid:
            success, err = __validate_file_existence(uuid, file_name)
            if not success:
                return success, err

    exists = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    if exists is not None:
        return False, "Dataset with that name already been created"

    isSuccess, error = __validate_new_dataset(rawDataUuid, vmapUuid, entitiesUuid)
    if not isSuccess:
        return isSuccess, error

    __create_directory_for_dataset(dataset_name)
    try:
        __move_files(dataset_name, rawDataUuid, vmapUuid, entitiesUuid)
        __save_metadata(
            dataset_name=dataset_name,
            category=category,
            dataset_source=dataset_source,
            description=description,
            public_private=public_private,
        )
    except Exception as e:
        __delete_directory_for_dataset(dataset_name)
        raise e
    # TODO: Add step - Zip files

    return True, "Dataset uploaded successfully"


def __move_and_unzip(dataset_name, visualization_id, zip_uuid):
    directory = os.path.join(__get_dataset_dir_path(dataset_name), "visualizations")
    path = os.path.join(directory, dataset_name)

    try:
        os.makedirs(directory, exist_ok=True)
        src_path = os.path.join(current_app.config["TEMP_PATH"], zip_uuid)
        shutil.copy(src_path, path)
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(os.path.join(directory, visualization_id))
        os.remove(path)
    except Exception as e:
        current_app.logger.error(e)
        __delete_directory_for_dataset(dataset_name)
        raise e

    return True


def import_dataset(dataset_name, description, dataset_source, public_private, category, zip_uuid):
    dataset_name = secure_filename(dataset_name)

    success, err = __validate_file_existence(zip_uuid, "zip")
    if not success:
        return success, err

    if dataset_name == "":
        return False, "Invalid dataset name"

    exists = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    if exists is not None:
        return False, "Dataset with that name already been created"

    visualization_id = str(uuid.uuid4())
    __create_directory_for_dataset(dataset_name)
    __move_and_unzip(dataset_name, visualization_id, zip_uuid)
    try:
        __save_metadata(
            category=category,
            dataset_name=dataset_name,
            dataset_source=dataset_source,
            description=description,
            public_private=public_private,
        )
        try:
            run = models.run(id=str(uuid.uuid4()), finished=True, success=True)
            new_vis = models.Visualization(id=visualization_id, dataset=dataset_name, run=run.id)
            db = get_db()
            db.session.add(run)
            db.session.commit()
            db.session.add(new_vis)
            db.session.commit()
        except Exception as e:
            db = get_db()
            db.session.rollback()
            dataset = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
            if dataset:
                db.session.delete(dataset)
                db.session.commit()
            raise e

    except Exception as e:
        __delete_directory_for_dataset(dataset_name)
        raise e

    return True, "Dataset imported successfully"
