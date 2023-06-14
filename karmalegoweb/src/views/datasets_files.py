import os

from flask import request
from flask import Blueprint, request, jsonify, current_app, send_file
from karmalegoweb.src import models
from karmalegoweb.src.views.auth import login_required
from karmalegoweb.src import utils

bp = Blueprint("datasets_files", __name__, "/")


@bp.route("/getDatasetFiles", methods=["GET"])
@login_required
def get_dataset_files():
    """
    This function handles a download request for a dataset's files.
    :param current_user: The user which is currently logged in.
    param dataset_id: the name of the dataset
    :return:
    500 (INTERNAL SERVER ERROR) if:
    # Any of the requested files could not be found in the server.

    200 (OK) if all files exist, returns a zipped folder of all the dataset files.
    """
    dataset_name = request.args.get("dataset_id")

    dataset_path = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name)

    if os.path.exists(dataset_path):
        files_to_send = [dataset_name + ".csv", "VMap.csv"]
        if os.path.exists(os.path.join(dataset_path, "Entities.csv")):
            files_to_send.append("Entities.csv")
    else:
        return jsonify({"message": "cannot find the requested data file in the server"}), 500

    data_zip_name = dataset_name + ".zip"

    utils.create_disc_zip(dataset_path, data_zip_name, files_to_send)

    return send_file(os.path.join(dataset_path, data_zip_name))


@bp.route("/getVMapFile", methods=["GET"])
@login_required
def get_vmap_file():
    """
    Returns the variable map file of a requested dataset.
    param id: the name of the dataset
    :return:
    404 (NOT FOUND) if:
    # The requested file cannot be found in the server.

    200 (OK) if the file exists, returns the variable map file
    """
    try:
        dataset_name = request.args.get("datasetName")
        return (
            send_file(current_app.config["DATASETS_ROOT"] + "/" + dataset_name + "/" + "VMap.csv"),
            200,
        )
    except FileNotFoundError:
        return jsonify({"message": "the request VMap file cannot be found."}), 400


@bp.route("/getRawDataFile", methods=["GET"])
@login_required
def get_raw_data_file():
    """
    :return: Returns a raw data file with the requested dataset id
    """
    dataset_name = request.args.get("id")
    return (
        send_file(
            current_app.config["DATASETS_ROOT"] + "/" + dataset_name + "/" + dataset_name + ".csv"
        ),
        200,
    )


@bp.route("/getEntitiesFile", methods=["GET"])
@login_required
def get_entities_file():
    """
    :return:
    404 (NOT FOUND) if:
    # The entity file cannot be found.

    200 (OK) if the file exists, Returns an entity file with the requested dataset id
    """
    dataset_name = request.args.get("id")
    if os.path.exists(os.path.join(current_app.config["DATASETS_ROOT"], dataset_name)):
        try:
            return (
                send_file(
                    current_app.config["DATASETS_ROOT"] + "/" + dataset_name + "/" + "Entities.csv"
                ),
                200,
            )
        except FileNotFoundError:
            return jsonify({"message": "the current dataset file has no entities file."}), 206
    else:
        return jsonify({"message": "the request Entities file cannot be found."}), 404
    
@bp.route("/getStatesFile", methods=["GET"])
@login_required
def get_states_file():
    """
    param dataset_id: the id of the dataset, string
    param disc_id: the id of the discretization, string
    :return:
    404 (NOT FOUND) if:
    # The states file cannot be found.

    200 (OK) if the file exists, Returns a states file with the requested dataset id and disc id
    """
    try:
        dataset_name = request.args.get("dataset_id")
        disc_name = request.args.get("disc_id")
        return (
            send_file(
                current_app.config["DATASETS_ROOT"]
                + "/"
                + dataset_name
                + "/"
                + disc_name
                + "/"
                + "states.csv"
            ),
            200,
        )
    except FileNotFoundError:
        return jsonify({"message": "the request States file cannot be found."}), 404


@bp.route("/getKLOutput", methods=["GET"])
@login_required
def get_kl_file():
    try:
        """
        param dataset_id: the id of the dataset
        param disc_id: the id of the discretization
        param kl_id: the id of the karmalego output
        :return:
        404 (NOT FOUND) if:
        # No KL output file can be found.

        200 (OK) if the file can be found, sends a KL output file.
        If the 'class' argument is present in the URL, sends the KL output file of the requested class.
        """
        dataset_name = request.args.get("dataset_id")
        # global disc_name
        disc_name = request.args.get("disc_id")
        # global kl_name
        kl_name = request.args.get("kl_id")
        if "class" in request.args.keys():
            kl_class = request.args.get("class")
            return (
                send_file(
                    current_app.config["DATASETS_ROOT"]
                    + "/"
                    + dataset_name
                    + "/"
                    + disc_name
                    + "/"
                    + kl_name
                    + "/"
                    + "KL-class-"
                    + kl_class
                    + ".0.txt"
                ),
                200,
            )
        return (
            send_file(
                current_app.config["DATASETS_ROOT"]
                + "/"
                + dataset_name
                + "/"
                + disc_name
                + "/"
                + kl_name
                + "/KL.txt"
            ),
            200,
        )
    except FileNotFoundError:
        return jsonify({"message": "the request KarmaLego output file cannot be found."}), 404
