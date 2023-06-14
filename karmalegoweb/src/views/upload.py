import os
from flask import Blueprint, current_app, request, jsonify

from karmalegoweb.src import upload_manager
from karmalegoweb.src.files_validation.raw_data import get_properties_list
from karmalegoweb.src.views.error_handlers import validate_args
from karmalegoweb.src.views.auth import login_required

# TODO: Switch later prefix
bp = Blueprint("upload", __name__, "")


@bp.route("/upload", methods=["POST"])
@login_required
@validate_args(
    [
        "datasetName",
        "description",
        "publicPrivate",
        "category",
        "datasetSource",
        "rawDataUuid",
        "vmapUuid",
    ]
)
def upload():
    """
    This function handles an upload of a new dataset.
    :param datasetName - the name of the dataset, string
    :param category - the category of the dataset, string
    :param publicPrivate - wether it public or private, string
    :param file - the dataset itself, csv
    :param description - the description of the dataset, string
    :param datasetSource - the source of the dataset, string
    :return:
    """
    # TODO: Validate uuid existese
    # TODO: Validate uuid ownership
    isSuccess, msg = upload_manager.upload_new_dataset(
        category=request.form["category"],
        dataset_name=request.form["datasetName"],
        dataset_source=request.form["datasetSource"],
        description=request.form["description"],
        entitiesUuid=request.form["entitiesUuid"] if "entitiesUuid" in request.form else None,
        public_private=request.form["publicPrivate"],
        rawDataUuid=request.form["rawDataUuid"],
        vmapUuid=request.form["vmapUuid"],
    )
    status = 200 if isSuccess else 400
    return msg, status


@bp.route("/import_data", methods=["POST"])
@login_required
@validate_args(
    ["datasetName", "description", "publicPrivate", "category", "datasetSource", "zipUuid"]
)
def import_data():
    # TODO: Validate uuid existese
    # TODO: Validate uuid ownership
    isSuccess, msg = upload_manager.import_dataset(
        category=request.form["category"],
        dataset_name=request.form["datasetName"],
        dataset_source=request.form["datasetSource"],
        description=request.form["description"],
        public_private=request.form["publicPrivate"],
        zip_uuid=request.form["zipUuid"],
    )
    status = 200 if isSuccess else 400
    return msg, status


@bp.route("/getVariableList", methods=["GET"])
@login_required
def get_variable_list_request():
    """
    This function handles a request for a dataset's variable list
    param dataset_id: the id of the dataset
    :return: A list of all the variables in a certain dataset
    """
    dataset_name = request.args.get("dataset_id")
    raw_data_path = os.path.join(
        current_app.config["DATASET_ROOT"], dataset_name, dataset_name + ".csv"
    )
    if not os.path.exists(raw_data_path):
        return "Requested dataset does not exists", 400

    properties = get_properties_list(raw_data_path)
    return jsonify({"VMapList": properties})
