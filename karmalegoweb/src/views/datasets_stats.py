import json, os, shutil

from flask import request
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import false

from karmalegoweb.src.views.error_handlers import validate_args
from karmalegoweb.src import models
from karmalegoweb.src.db import get_db
from karmalegoweb.src.views.auth import login_required

bp = Blueprint("datasets_stats", __name__, "/")


# sends all the info about the data sets
@bp.route("/getAllDataSets", methods=["GET"])
@login_required
def get_all_datasets():
    """
    Returns info on all datasets in the server.
    :return:
    500 (INTERNAL SERVER ERROR) if:
    # There has been an unexpected server error.

    200 (OK) if all went well, the response contains:
    # lengthNum: The number of datasets
    # A table that contains metadata about each dataset in the system.
    """
    datasets = models.info_about_datasets.query.filter_by(uploaded=True).all()
    to_return = {}
    x = 0
    to_return["lengthNum"] = len(datasets)
    for curr_dataset in datasets:
        full_name = curr_dataset.owner.FName + " " + curr_dataset.owner.LName
        to_return[str(x)] = {
            "Category": curr_dataset.category,
            "DatasetName": curr_dataset.Name,
            "Owner": full_name,
            "PublicPrivate": curr_dataset.public_private,
            "Size": str(curr_dataset.size),
        }
        x = x + 1

    return jsonify(to_return)


@bp.route("/getInfo", methods=["GET"])
@login_required
def get_all_info_on_dataset():
    """
    param id: the name of the dataset
    Returns all the information on a requested dataset.
    :return: A JSON object with the info about a dataset.
    """
    dataset_name = request.args.get("datasetName")
    info = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    if info is None:
        return "Dataset does not exists", 400
    return (
        jsonify(
            {
                "category": info.category,
                "Description": info.Description,
                "downloads": info.downloads,
                "Name": info.Name,
                "owner_name": info.Email,
                "size": str(info.size) + " MB",
                "source": info.source,
                "views": info.views,
                "class_0_name": info.class_0_name,
                "class_1_name": info.class_1_name,
            }
        ),
        200,
    )


@bp.route("/getDataOnDataset", methods=["GET"])
@validate_args(["datasetName"], False)
def get_data_on_dataset():
    """
    This function returns all of the existing discretization and KL runs for a given dataset.
    param id: the name of the dataset
    :return:the data on a specific dataset
    """
    dataset_name = request.args.get("datasetName")
    if check_for_authorization(g.user, dataset_name):
        return jsonify({"message": "don't try to fool me, you don't own it!"}), 403

    discretizations = models.discretization.query.filter_by(dataset_Name=dataset_name).all()

    def model_to_discretization(model):
        status = models.discretization_status.query.filter_by(discretization_id=model.id).first()
        return {
            "BinsNumber": str(model.NumStates),
            "id": str(model.id),
            "InterpolationGap": str(model.InterpolationGap),
            "MethodOfDiscretization": str(model.AbMethod),
            "PAAWindowSize": str(model.PAA),
            "status": {"finished": status.finished, "success": status.success},
        }

    disc_to_return = list(map(model_to_discretization, discretizations))

    karma_arr = []
    negative_arr = []
    for curr_disc in discretizations:
        karma_arr.extend(models.karma_lego.query.filter_by(discretization=curr_disc).all())

    for curr_disc in discretizations:
        negative_arr.extend(models.negative_karma_lego.query.filter_by(discretization=curr_disc).all())

    def model_to_TIM(model):
        status = models.karmalego_status.query.filter_by(karmalego_id=model.id).first()
        return {
            "BinsNumber": str(model.discretization.NumStates),
            "discId": model.discretization.id,
            "epsilon": str(model.epsilon),
            "indexSame": str(model.index_same),
            "InterpolationGap": str(model.discretization.InterpolationGap),
            "karma_id": str(model.id),
            "MaxGap": str(model.max_gap),
            "maxTirpLength": str(model.max_tirp_length),
            "MethodOfDiscretization": str(model.discretization.AbMethod),
            "numRelations": str(model.num_relations),
            "PAAWindowSize": str(model.discretization.PAA),
            "VerticalSupport": str(model.min_ver_support),
            "status": {"finished": status.finished, "success": status.success},
        }
    
    def negative_to_TIM(model):
        status = models.karmalego_status.query.filter_by(karmalego_id=model.id).first()
        return {
            "discId": model.discretization.id,
            "BinsNumber": str(model.discretization.NumStates),
            "InterpolationGap": str(model.discretization.InterpolationGap),
            "MethodOfDiscretization": str(model.discretization.AbMethod),
            "PAAWindowSize": str(model.discretization.PAA),
            "karma_id": str(model.id),
            "MaxGap": str(model.max_gap),
            "VerticalSupport": str(model.min_ver_support),
            "MaximumNegatives": str(model.maximum_negatives),
            "ofo": str(model.ofo),
            "as": str(model.a_s),
            "bc": str(model.bc),
            "status": {"finished": status.finished, "success": status.success},
        }

    karma_to_return = list(map(model_to_TIM, karma_arr))

    negatives_to_return = list(map(negative_to_TIM, negative_arr))

    return jsonify({"disc": disc_to_return, "karma": karma_to_return, "negative": negatives_to_return})
    
@bp.route("/getIsSequential", methods=["GET"])
@validate_args(["datasetName"], False)
def get_is_sequential_dataset():
    """
    This function returns all of the existing discretization and KL runs for a given dataset.
    param id: the name of the dataset
    :return:the data on a specific dataset
    """
    dataset_name = request.args.get("datasetName")
    if check_for_authorization(g.user, dataset_name):
        return jsonify({"message": "don't try to fool me, you don't own it!"}), 403
    
    file = dataset_name + ".ascii"

    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        dataset_name,
        file
    )

    def is_ascii_file(file_path):
        print(file_path)
        return os.path.exists(file_path)
    
    is_sequential = is_ascii_file(path)
    
    return jsonify({"answer": is_sequential})


@bp.route("/incrementViews", methods=["POST"])
@login_required
def increment_views():
    """
    Increases the view count of a dataset by 1.
    :param datset_id: the id of the dataset we want to increment his views, int
    :return: the new number of views in the database
    """
    dataset_name = request.form["datasetName"]
    dataset = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    if dataset is None:
        return jsonify({"message": "dataset does not exists", "views": 0}), 400
    views = dataset.views + 1
    dataset.views = views
    db = get_db()
    db.session.commit()

    return jsonify({"message": "success", "views": views}), 200


@bp.route("/deleteDataset", methods=["POST"])
@login_required
@validate_args(["datasetName"])
def deleteDataset():
    """
    Increases the view count of a dataset by 1.
    :param datset_id: the id of the dataset we want to increment his views, int
    :return: the new number of views in the database
    """
    dataset_name = request.form["datasetName"]
    dataset = models.info_about_datasets.query.filter_by(Name=dataset_name).first()

    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        request.form["datasetName"],
    )
    if not os.path.exists(path):
        return "dataset found but could not find the dataset folder", 500
    discretizations = models.discretization.query.filter_by(dataset_Name=dataset_name)
    descritization_statuses = []
    for disc in discretizations:
        descritization_statuses.append(
            models.discretization_status.query.filter_by(discretization_id=disc.id).first()
        )

    discretization_paths = []
    for disc in discretizations:
        path = os.path.join(
            current_app.config["DATASETS_ROOT"],
            request.form["datasetName"],
            disc.id,
        )
        discretization_paths.append(path)

    karmalegos_objects = []
    karmalego_status_objects = []
    if discretizations is not None:
        for disc in discretizations:
            karmalegos = models.karma_lego.query.filter_by(discretization_name=disc.id)
            if karmalegos is None:
                karmalegos = models.negative_karma_lego.query.filter_by(discretization_name=disc.id)
            if karmalegos is not None:
                karmalegos_objects += karmalegos
                for kl in karmalegos:
                    karmalego_status = models.karmalego_status.query.filter_by(karmalego_id=kl.id)
                    karmalego_status_objects += karmalego_status

    visualization_paths = []
    visualizations = models.Visualization.query.filter_by(dataset=dataset_name)
    for visualization in visualizations:
        visualization_path = os.path.join(
            current_app.config["DATASETS_ROOT"],
            dataset_name,
            "visualizations",
            visualization.id,
        )
        visualization_paths.append(visualization_path)

    db = get_db()
    for visualization in visualizations:
        db.session.delete(visualization)
    for visual_path in visualization_paths:
        shutil.rmtree(visual_path)

    for karmalego in karmalegos_objects:
        db.session.delete(karmalego)
    for karmalego_status in karmalego_status_objects:
        db.session.delete(karmalego_status)

    for disc in discretizations:
        db.session.delete(disc)
    for disc_ststus in descritization_statuses:
        db.session.delete(disc_ststus)
    for disc_path in discretization_paths:
        shutil.rmtree(disc_path)
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        request.form["datasetName"],
    )
    shutil.rmtree(dataset_path)
    db.session.delete(dataset)
    db.session.commit()

    return jsonify({"message": "success"}), 200


@bp.route("/incrementDownload", methods=["POST"])
@login_required
def increment_download():
    """
    Increases the download count of a dataset by 1.
    :param datset_id: the id of the dataset we want to increment his downloads
    :return: the new number of downloads in the database
    """
    dataset_name = request.form["dataset_id"]
    dataset = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    if dataset is None:
        return jsonify({"message": "dataset does not exists", "downloads": 0}), 400
    download = dataset.downloads + 1
    dataset.downloads = download
    db = get_db()
    db.session.commit()

    return jsonify({"message": "success", "downloads": download}), 200


@bp.route("/getVisualizations", methods=["GET"])
@login_required
def get_visualizations():
    visualizations = models.Visualization.query.all()
    data_sets_details = list()
    for visualization in visualizations:
        run = models.run.query.filter_by(id=visualization.run).first()
        info = models.info_about_datasets.query.filter_by(Name=visualization.dataset).first()
        user = models.Users.query.filter_by(Email=info.Email).first()

        if run.finished:
            settings = {
                "data_set_name": info.Name,
                "category": info.category,
                "size": info.size,
                "permission": info.Permissions,
                "description": info.Description,
                "owner": f"{user.FName} {user.LName}",
                "id": visualization.id,
                "imported": visualization.KL_id is None,
            }

            if run.success:
                path = os.path.join(
                    current_app.config["DATASETS_ROOT"],
                    visualization.dataset,
                    "visualizations",
                    visualization.id,
                )
                settings_path = os.path.join(path, "settings.json")

                if os.path.exists(settings_path):
                    with open(settings_path, "r") as fs:
                        settings.update(json.load(fs))
                    settings["success"] = True
                else:
                    current_app.logger.warning("Could not find settings file for visualization")
                    settings["success"] = False
            else:
                settings["success"] = False
            data_sets_details.append(settings)

    return jsonify({"DataSets": data_sets_details})


@bp.route("/getVisualizationInfo", methods=["GET"])
@login_required
@validate_args(["visualization_id"], False)
def get_visualization_info():
    visualization_id = request.args.get("visualization_id")
    visualization = models.Visualization.query.filter_by(id=visualization_id).first()
    if not visualization:
        return "Request visualization could not be found", 400

    info = models.info_about_datasets.query.filter_by(Name=visualization.dataset).first()
    user = models.Users.query.filter_by(Email=info.Email).first()

    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        visualization.dataset,
        "visualizations",
        visualization.id,
    )
    settings_path = os.path.join(path, "settings.json")

    settings = {}
    with open(settings_path, "r") as fs:
        settings = json.load(fs)
        settings["data_set_name"] = info.Name
        settings["category"] = info.category
        settings["size"] = info.size
        settings["permission"] = info.Permissions
        settings["description"] = info.Description
        settings["owner"] = f"{user.FName} {user.LName}"
        settings["id"] = visualization.id
        settings["imported"] = visualization.KL_id is None
        settings["class_0_name"] = info.class_0_name
        settings["class_1_name"] = info.class_1_name

    return jsonify(settings)


@bp.route("/getVisualizationDetails", methods=["GET"])
@login_required
@validate_args(["visualization_id"], False)
def get_visualization_details():
    visualization_id = request.args.get("visualization_id")
    visualization = models.Visualization.query.filter_by(id=visualization_id).first()
    if not visualization:
        return "Request visualization could not be found", 400
    if visualization.KL_id is None:
        return "There is no visualization details on an imported dataset", 400
    karmalego = models.karma_lego.query.filter_by(id=visualization.KL_id).first()
    if karmalego is not None:
        discretization = models.discretization.query.filter_by(id=karmalego.discretization_name).first()

        karmalego_details = {
            "min_ver_support": karmalego.min_ver_support,
            "num_relations": karmalego.num_relations,
            "max_gap": karmalego.max_gap,
            "max_tirp_length": karmalego.max_tirp_length,
            "index_same": karmalego.index_same,
            "epsilon": karmalego.epsilon,
        }
        discretization_details = {
            "paa": discretization.PAA,
            "method": discretization.AbMethod,
            "number_of_bins": discretization.NumStates,
            "interpolation_gap": discretization.InterpolationGap,
        }

        return jsonify({"karmalego": karmalego_details, "discretization": discretization_details})
    
    else:
        karmalego = models.negative_karma_lego.query.filter_by(id=visualization.KL_id).first()
        discretization = models.discretization.query.filter_by(id=karmalego.discretization_name).first()

        karmalego_details = {
            "min_ver_support": karmalego.min_ver_support,
            "max_gap": karmalego.max_gap,
            "maximun_negatives" : karmalego.maximum_negatives,
        }
        discretization_details = {
            "paa": discretization.PAA,
            "method": discretization.AbMethod,
            "number_of_bins": discretization.NumStates,
            "interpolation_gap": discretization.InterpolationGap,
        }

        return jsonify({"karmalego": karmalego_details, "discretization": discretization_details})



def check_for_authorization(current_user, dataset_name):
    """
    This function verifies the authorization of the current user on a given dataset.
    she gets the current user by his id and the dataset name
    :param current_user: the email of the current user
    :param dataset_name: the name of the dataset
    :return:
    """
    per = models.Permissions.query.filter_by(
        name_of_dataset=dataset_name, Email=current_user.Email
    ).first()
    dataset = models.info_about_datasets.query.filter_by(Name=dataset_name).first()
    if dataset is None:
        return false
    if dataset.public_private == "Public":
        return False

    if (per is None or current_user.Email != per.owner.Email) and (
        dataset.owner.Email != current_user.Email
    ):
        return True
    else:
        return False
