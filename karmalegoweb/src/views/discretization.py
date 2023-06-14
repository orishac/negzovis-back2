from collections import defaultdict
import csv
import os, shutil

from flask import current_app, Blueprint, request, jsonify, send_file, g

from karmalegoweb.src.discretization.concrete_builders.gradient import gradient
from karmalegoweb.src.discretization.concrete_builders.abstraction_per_property import (
    abstraction_per_property,
)
from karmalegoweb.src.discretization.concrete_builders.knowledge_base import (
    knowledge_based,
)
from karmalegoweb.src.discretization.concrete_builders.traditional_discretization import (
    equal_frequency,
    equal_width,
    kmeans,
    persist,
    sax,
    td4c_cosine,
    td4c_diffmax,
    td4c_diffsum,
    td4c_entropy,
    td4c_entropy_ig,
    td4c_skl,
    empty
)


from karmalegoweb.src.tasks import discretization
from karmalegoweb.src.views.error_handlers import validate_args
from karmalegoweb.src.db import get_db
from karmalegoweb.src.views.auth import login_required
from karmalegoweb.src import models, utils

bp = Blueprint("discretization", __name__, "/")


@bp.route("/addNewDisc", methods=["POST"])
@login_required
@validate_args(["AbMethod"])
def add_new_disc():
    """
    This function handles a submission of a new discretization to the system.
    :param PAA
    :param NumStates - the number of states we want to send to discretization, int
    :param InterpolationGap - the interpolation gap variable we want to send to discretization , float
    :param AbMethod - the abstract mathod we want to send to discretization, string
    :param KnowledgeBasedFile - if there is a knowledge-based file we send it as well, csv file
    :param GradientFile - if there is a gradient file we send it as well, csv file
    :param GradientWindowSize - if there is a gradient file we send its window size, float
    :param PreprocessingFile - A csv file that describes the preprocessing per property in per property method
    :param AbstractionMethodFile - A csv file that describes the abstraction method per property in per property method
    :param StatesFile - A csv file that describes the bins for knowledge base discretizations in per property method
    :return:
    400 (BAD REQUEST) if:
    # One of the user inputs are invalid (empty/incorrect).
    # The Knowledge-based/Gradient file did not go through the validations successfully (incorrect format/not unique).
    # The user requested a TD4C discretizations and did so on a dataset with no classes.
    # The same discretization already exists in the system.

    409 (CONFLICT) if:
    # The server cannot send an email.

    500 (INTERNAL SERVER ERROR) if:
    # The discretization system has failed to create the necessary files.

    200 (OK) if all went well
    """
    form = request.form
    files = request.files

    paa = int(form["PAA"]) if "PAA" in form else 0
    abstraction_method = form["AbMethod"] if "AbMethod" in form else None
    interpolation_gap = int(form["InterpolationGap"]) if "InterpolationGap" in form else None
    dataset_name = form["datasetName"] if "datasetName" in form else None
    numStates = int(form["NumStates"]) if "NumStates" in form else None
    gradient_window_size = int(form["GradientWindowSize"]) if "GradientWindowSize" in form else None
    bins_names = form["binsNames"] if "binsNames" in form else None

    gradient_file = files["GradientFile"] if "GradientFile" in files else None
    preprocessing_file = files["PreprocessingFile"] if "PreprocessingFile" in files else None
    abstraction_method_file = (
        files["AbstractionMethodFile"] if "AbstractionMethodFile" in files else None
    )
    states_file = files["StatesFile"] if "StatesFile" in files else None
    knowledge_based_file = files["KnowledgeBasedFile"] if "KnowledgeBasedFile" in files else None

    builder = None
    result = False, f"You have requested an unknown abstraction method: {abstraction_method}"
    try:
        if abstraction_method == "Equal Frequency":
            builder = equal_frequency(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "Equal Width":
            builder = equal_width(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "SAX":
            builder = sax(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "Persist":
            builder = persist(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "KMeans":
            builder = kmeans(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "TD4C-Cosine":
            builder = td4c_cosine(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "TD4C-Diffmax":
            builder = td4c_diffmax(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "TD4C-Diffsum":
            builder = td4c_diffsum(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "TD4C-Entropy":
            builder = td4c_entropy(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "TD4C-Entropy-IG":
            builder = td4c_entropy_ig(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "TD4C-SKL":
            builder = td4c_skl(dataset_name)
            result = builder.make(interpolation_gap, paa, numStates)
        elif abstraction_method == "Gradient":
            builder = gradient(dataset_name)
            result = builder.make(interpolation_gap, paa, gradient_window_size, gradient_file, numStates)
        elif abstraction_method == "Knowledge-Based":
            builder = knowledge_based(dataset_name)
            result = builder.make(interpolation_gap, paa, knowledge_based_file)
        elif abstraction_method == "Abstraction Per Property":
            builder = abstraction_per_property(dataset_name)
            result = builder.make(preprocessing_file, states_file, abstraction_method_file)
        elif abstraction_method == "Sequential":
            builder = empty(dataset_name)
            result = builder.make()

        if not result[0]:
            return result[1], 400

        discretization(
            list(files.keys()),
            abstraction_method == "Abstraction Per Property",
            abstraction_method == "Sequential",
            dataset_name,
            builder.id,
            bins_names,
            g.user.Email,
            builder.get_hugobot_command(),
            builder.disc_path,
            builder.dataset_path,
        )
        
        # args = [
        #     list(files.keys()),
        #     abstraction_method == "Abstraction Per Property",
        #     dataset_name,
        #     builder.id,
        #     bins_names,
        #     g.user.Email,
        #     builder.get_hugobot_command(),
        #     builder.disc_path,
        #     builder.dataset_path,
        # ]
        # discretization.apply_async(args=args)

        db = get_db()
        db.session.commit()

    except Exception as e:
        if builder is not None and os.path.exists(builder.disc_path):
            shutil.rmtree(builder.disc_path)
        db = get_db()
        db.session.rollback()
        raise e

    return builder.id, 200


@bp.route("/getDISC", methods=["POST"])
@login_required
def get_disc():
    """
    This function handles a request to download a zip of all the discretization files.
    :param current_user: The user which is currently logged in.
    param: disc_id: the discretization id that we want to get data on
    :return:
    500 (INTERNAL SERVER ERROR) if:
    # The server cannot find any of the requested files

    200 (OK) if all files have been found, sends a zipped folder of all the HugoBot system's outputs.
    """
    data = request.form
    disc_id = data["disc_id"]
    disc = models.discretization.query.filter_by(id=disc_id).first()
    # if check_for_bad_user_disc(disc, current_user.Email):
    #     return jsonify({'message': 'don't try to fool me, you don't own it!'}), 400
    dataset = disc.dataset.Name

    disc_path = os.path.join(current_app.config["DATASETS_ROOT"], dataset, disc_id)

    # states_file_name = "states.csv"  # first try finding a regular states file

    # if not os.path.exists(os.path.join(disc_path, states_file_name)):
    #     states_file_name = "states_kb_gradient.csv"  # try gradient
    #     if not os.path.exists(os.path.join(disc_path, states_file_name)):
    #         states_file_name = "states_kb.csv"  # try knowledge-based
    #         if not os.path.exists(os.path.join(disc_path, states_file_name)):
    #             return (
    #                 jsonify({"message": "cannot find the requested states file in the server"}),
    #                 500,
    #             )

    disc_zip_name = "discretization.zip"
    flag = True
    if os.path.exists(os.path.join(disc_path, "states.csv")):
        flag = False
        states_file_name = "states.csv"
    if os.path.exists(os.path.join(disc_path, "states_kb_gradient.csv")):
        states_file_name = "states_kb_gradient.csv"
        flag = False
    if os.path.exists(os.path.join(disc_path, "states_kb.csv")):
        states_file_name = "states_kb.csv"
        flag = False
    if flag:
        return (
                    jsonify({"message": "cannot find the requested states file in the server"}),
                    500,
                )

    files_to_send = [
        "entity-class-relations.csv",
        "KL.txt",
        "prop-data.csv",
        states_file_name,
        "symbolic-time-series.csv",
    ]

    if os.path.exists(os.path.join(disc_path, "KL-class-0.0.txt")) and os.path.exists(
        os.path.join(disc_path, "KL-class-1.0.txt")
    ):
        files_to_send.append("KL-class-0.0.txt")
        files_to_send.append("KL-class-1.0.txt")

    utils.create_disc_zip(disc_path, disc_zip_name, files_to_send)

    return send_file(os.path.join(disc_path, disc_zip_name))


@bp.route("/deleteDescritization", methods=["POST"])
def delete_descritization():
    descritization = models.discretization.query.filter_by(id=request.form["disc_id"]).first()
    if descritization is None:
        return "Could not found requested descretization", 400
    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        request.form["datasetName"],
        request.form["disc_id"],
    )
    if os.path.exists(path):
        shutil.rmtree(path)

    descritization_status = models.discretization_status.query.filter_by(
        discretization_id=request.form["disc_id"]
    ).first()
    karmalegos = models.karma_lego.query.filter_by(discretization_name=request.form["disc_id"])

    karmalegos_statuses = []
    karmalegos_paths = []
    visualizations_paths = []
    visualizations_total = []
    if karmalegos is not None:
        for karmalego in karmalegos:
            karmalego_path = os.path.join(
                current_app.config["DATASETS_ROOT"],
                request.form["datasetName"],
                request.form["disc_id"],
                karmalego.id,
            )
            karmalegos_paths.append(karmalego_path)
            karmalego_status = models.karmalego_status.query.filter_by(
                karmalego_id=karmalego.id
            ).first()
            karmalegos_statuses.append(karmalego_status)
            visualizations = models.Visualization.query.filter_by(KL_id=karmalego.id)
            if visualizations is not None:
                for visualization in visualizations:
                    visualization_path = os.path.join(
                        current_app.config["DATASETS_ROOT"],
                        request.form["datasetName"],
                        "visualizations",
                        visualization.id,
                    )
                    visualizations_paths.append(visualization_path)
                    visualizations_total.append(visualization)

    db = get_db()
    for visualization in visualizations_total:
        db.session.delete(visualization)
    for visual_path in visualizations_paths:
        if os.path.exists(visual_path):
            shutil.rmtree(visual_path)

    for karmalego_status in karmalegos_statuses:
        db.session.delete(karmalego_status)
    for karmalego_path in karmalegos_paths:
        if os.path.exists(karmalego_path):
            shutil.rmtree(karmalego_path)

    for karmalego in karmalegos:
        db.session.delete(karmalego)
    for karmalego_path in karmalegos_paths:
        if os.path.exists(karmalego_path):
            shutil.rmtree(karmalego_path)

    db.session.delete(descritization)
    db.session.delete(descritization_status)
    db.session.commit()
    return "Deleted discretization successfully"

