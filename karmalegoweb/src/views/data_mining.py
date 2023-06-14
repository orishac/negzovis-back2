import uuid
import os, shutil

from flask import current_app, g, Blueprint, request, jsonify, send_file

from karmalegoweb.src.preprocessing.results import preprocessins_results
from karmalegoweb.src.preprocessing.preproccessing import preprocessing

from karmalegoweb.src.views.error_handlers import validate_args
from karmalegoweb.src.views.auth import login_required
from karmalegoweb.src.db import get_db
from karmalegoweb.src import models, tasks, utils

from karmalegoweb.KarmaLego_Framework import RunKarmaLego


bp = Blueprint("data_mining", __name__, "/")


@bp.route("/addTIM", methods=["POST"])
@login_required
@validate_args(
    [
        "DiscretizationId",
        "Epsilon",
        "Max Gap",
        "min_ver_support",
        "num_relations",
        "max Tirp Length",
        "index_same",
    ]
)
def add_tim():
    """
    This function handles a new KarmaLego run attempt.
    :param current_user: The user which is currently logged in.
    param - epsilon - the value of epsilon, int
    param - max gap- int, the max_gap between the intervals for creating the index
    :param min_ver_support: float, the minimum vertical support value
    :param num_relations: int, number of relations
    :param index_same: Boolean, index same symbols or not
    :return:
    if it was a sussess run it returns status 200
    if there is already a karma lego like the user wants now it returns status 400
    """
    # makes all the validations e making any write to the database
    data = request.form
    # if check_if_not_int_but_0(data['Epsilon']):
    #     return jsonify({'message': 'you did not give me an integer but a float'}), 404
    # if check_if_not_int(data['max Tirp Length']) or check_if_not_int(
    #         data['Max Gap']) or check_if_not_int(data['min_ver_support']):
    #     return jsonify({'message': 'you did not give me an integer but a float or a number less then 1'}), 404
    # if int(data['min_ver_support']) > 100:
    #     return jsonify({'message': 'minimum vertical support cant be greater then 100'}), 404
    # discretization_id = str(data['DiscretizationId'])
    # if 'Epsilon' not in data:
    #     epsilon = int(0.0000)
    # else:
    #     epsilon = int(data['Epsilon'])
    # saves all the parameters that the user passed me
    discretization_id = data["DiscretizationId"]
    epsilon = int(data["Epsilon"])
    max_gap = int(data["Max Gap"])
    vertical_support = int(data["min_ver_support"]) / 100
    num_relations = int(data["num_relations"])
    max_tirp_length = int(data["max Tirp Length"])
    index_same = str(data["index_same"])
    class_name = str(data["class_name"])
    second_class_name = str(data["second_class_name"])
    timestamp = str(data["timestamp"])
    comments = str(data["comments"])
    to_visualize = data["to_visualize"]

    if index_same == "true":
        index_same = True
    else:
        index_same = False
    disc = models.discretization.query.filter_by(id=discretization_id).first()
    email = g.user.Email
    # checking if the current discretization already exists
    if check_exists(
        disc, epsilon, max_gap, vertical_support, num_relations, index_same, max_tirp_length
    ):
        return (
            jsonify(
                {
                    "message": "Time interval mining file for this dataset with the same parameters already exist"
                }
            ),
            409,
        )
    dataset_name = get_dataset_name(disc)
    # dataset_name ='Gradient'
    KL_id = str(uuid.uuid4())
    create_directory(dataset_name, discretization_id, KL_id)
    directory_path = dataset_name + "\\" + discretization_id
    # saves the data to the dataset
    KL = models.karma_lego(
        discretization=disc,
        epsilon=epsilon,
        id=KL_id,
        index_same=index_same,
        max_gap=max_gap,
        max_tirp_length=max_tirp_length,
        min_ver_support=vertical_support,
        num_relations=num_relations,
    )
    status = models.karmalego_status(karmalego_id=KL_id)
    db = get_db()
    db.session.add(KL)
    db.session.add(status)
    db.session.commit()

    # after creating the directory, creating by karma lego 3 files: kl, kl0, kl1
    try:
        for filename in os.listdir(current_app.config["DATASETS_ROOT"] + "\\" + directory_path):
            if filename.endswith(".txt"):
                path = current_app.config["DATASETS_ROOT"] + "\\" + directory_path + "\\" + filename

                out_path = (
                    current_app.config["DATASETS_ROOT"]
                    + "\\"
                    + directory_path
                    + "\\"
                    + KL_id
                    + "\\"
                    + filename[:-4]  # Removes the .txt
                )

                os.mkdir(out_path)

                # calling the actual karma lego algorithm
                _lego_0, _karma_0 = RunKarmaLego.runKarmaLego(
                    time_intervals_path=path,
                    output_path=out_path,
                    processes_num=10,
                    calc_offsets=True,
                    entity_ids_num=2,
                    epsilon=epsilon,
                    incremental_output=True,
                    index_same=index_same,
                    label=0,
                    max_gap=max_gap,
                    max_tirp_length=max_tirp_length,
                    min_ver_support=vertical_support,
                    need_one_sized=True,
                    num_comma=2,
                    num_relations=num_relations,
                    print_params=True,
                    semicolon_end=True,
                    skip_followers=False,
                )
            else:
                continue
    except Exception as e:
        current_app.log_exception(e)
        status.finished = True
        status.success = False
        db.session.commit()

        tasks.send_email(message=f"Subject: problem with creating karmalego", receiver_email=email)

        return jsonify({"message": "A problem as occurred with karmalego"}), 500
    # checks if the creation of the file of the karma lego was successful and if not it deletes the record from the db
    if (
        (
            os.path.exists(
                current_app.config["DATASETS_ROOT"]
                + "/"
                + directory_path
                + "/"
                + KL_id
                + "/"
                + "KL"
            )
        )
        or (
            os.path.exists(
                current_app.config["DATASETS_ROOT"]
                + "/"
                + directory_path
                + "/"
                + KL_id
                + "/"
                + "KL-class-0.0"
            )
        )
        or (
            os.path.exists(
                current_app.config["DATASETS_ROOT"]
                + "/"
                + directory_path
                + "/"
                + KL_id
                + "/"
                + "KL-class-1.0"
            )
        )
    ):
        status.finished = True
        status.success = True
        db.session.commit()
        tasks.send_email(message=f"Subject: karmalego successfully created", receiver_email=email)
        if to_visualize == "true":
            print("finished KL, starting Guy's preprocess")
            # call Guy's and Tali's preprocessing
            process = preprocessing(KL_id)
            result, _vis_id = process.start()
            if result != preprocessins_results.GOOD:
                tasks.send_email(
                    message=f"Subject: problem with preprocessing", receiver_email=email
                )
                return jsonify({"message": "A problem as occurred with preprocessing"}), 500

            print("finished Guy's and Tali's preprocess")

        return jsonify({"message": "karmalego created!", "KL_id": KL_id}), 200
    else:
        status.finished = True
        status.success = False
        db.session.commit()

        tasks.send_email(message=f"Subject: problem with creating karmalego", receiver_email=email)

        return jsonify({"message": "A problem as occurred with karmalego"}), 500


@bp.route("/deleteKarmaLego", methods=["POST"])
@login_required
@validate_args(["karma_id", "disc_id", "datasetName"])
def deleteKarmaLego():
    karmalego = models.karma_lego.query.filter_by(id=request.form["karma_id"]).first()
    if karmalego is None:
        return "Could not found requested karmalego", 400
    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        request.form["datasetName"],
        request.form["disc_id"],
        request.form["karma_id"],
    )
    if os.path.exists(path):
        shutil.rmtree(path)

    karmalego_status = models.karmalego_status.query.filter_by(
        karmalego_id=request.form["karma_id"]
    ).first()
    visualizations = models.Visualization.query.filter_by(KL_id=request.form["karma_id"])
    visualizations_paths = []
    for visualization in visualizations:
        visualization_path = os.path.join(
            current_app.config["DATASETS_ROOT"],
            request.form["datasetName"],
            "visualizations",
            visualization.id,
        )
        visualizations_paths.append(visualization_path)

    db = get_db()
    for visualization in visualizations:
        db.session.delete(visualization)
    for visual_path in visualizations_paths:
        if os.path.exists(visual_path):
            shutil.rmtree(visual_path)

    db.session.delete(karmalego)
    db.session.delete(karmalego_status)
    db.session.commit()

    return "Deleted karmalego successfully"


@bp.route("/getTIM", methods=["POST"])
@login_required
def get_tim():
    """
    This function handles a request to download a zip of all the karma lego files.
    :return:
    200 (OK) if all files have been found, sends a zipped folder of all the KarmaLego framework's outputs.
    """
    data = request.form
    kl_id = data["kl_id"]
    karma = models.karma_lego.query.filter_by(id=kl_id).first()
    disc = karma.discretization.id
    dataset = karma.discretization.dataset.Name

    kl_path = os.path.join(current_app.config["DATASETS_ROOT"], dataset, disc, kl_id)

    kl_zip_name = "karma_lego.zip"

    files_to_send = ["KL.txt"]

    if os.path.exists(os.path.join(kl_path, "KL-class-0.0.txt")):
        files_to_send.append("KL-class-0.0.txt")

    if os.path.exists(os.path.join(kl_path, "KL-class-1.0.txt")):
        files_to_send.append("KL-class-1.0.txt")

    utils.create_disc_zip(kl_path, kl_zip_name, files_to_send)

    return send_file(os.path.join(kl_path, kl_zip_name))


def check_exists(
    disc, epsilon, max_gap, vertical_support, num_relations, index_same, max_tirp_length
):
    """
    This function checks if a KL run already exists in the DB
    param - epsilon - the value of epsilon, int
    param - max gap- int, the max_gap between the intervals for creating the index
    :param min_ver_support: float, the minimum vertical support value
    :param num_relations: int, number of relations
    :param index_same: Boolean, index same symbols or not
    :return:
    if there is already a kl with that caracteristics
    """
    exists = models.karma_lego.query.filter_by(
        discretization=disc,
        epsilon=epsilon,
        index_same=index_same,
        max_gap=max_gap,
        max_tirp_length=max_tirp_length,
        min_ver_support=vertical_support,
        num_relations=num_relations,
    ).first()
    if exists is None:
        return False
    return True


def get_dataset_name(disc):
    """
    This function returns the dataset name for a given discretization.
    :param disc: the id of the discretization
    :return:
    the name of the dataset related to the discretization
    """
    dataset = disc.dataset
    dataset_name = dataset.Name
    return dataset_name


def create_directory(dataset_name, discretization_id, kl_id):
    """
    This function creates a directory for a KarmaLego run inside its parent discretization folder.
    :param dataset_name: the name of the datset
    :param discretization_id: the id of the discretization
    :param kl_id: the id of the karma lego run
    :return:
    """
    path = (
        current_app.config["DATASETS_ROOT"]
        + "/"
        + dataset_name
        + "/"
        + discretization_id
        + "/"
        + kl_id
    )
    try:
        os.mkdir(path)
    except OSError as e:
        current_app.log_exception(e)
    else:
        current_app.logger.info("Successfully created the directory %s " % path)
    return path
