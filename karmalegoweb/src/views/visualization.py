import ast
import csv
import os, json, shutil

from flask import Blueprint, request, jsonify, make_response, current_app

from karmalegoweb.src.preprocessing.tirp import tirp
from karmalegoweb.src.db import get_db
from karmalegoweb.src import models
from karmalegoweb.src.views.auth import login_required
from karmalegoweb.src.views.error_handlers import validate_args
from karmalegoweb.src.Visualization import ParseOutputFile, Index
from karmalegoweb.src.Visualization.SearchInIndexFile import SearchInIndexFile


bp = Blueprint("visualization", __name__, "/")


@bp.route("/deleteVisualization", methods=["POST"])
@login_required
@validate_args(["visualization"])
def delete_visualization():
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    run_id = visualization.run
    run = models.run.query.filter_by(id=run_id).first()

    if visualization is None:
        return "Could not found requested visualization", 400
    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        visualization.dataset,
        "visualizations",
        visualization.id,
    )
    if os.path.exists(path):
        shutil.rmtree(path)

    db = get_db()
    db.session.delete(visualization)
    if run:
        db.session.delete(run)
    db.session.commit()

    return "Deleted visualization successfully"


@bp.route("/getEntities", methods=["POST"])
@login_required
@validate_args(["visualization"])
def get_entities():
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    if visualization is None:
        return "Could not found requested visualization", 400

    visualization_path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        visualization.dataset,
        "visualizations",
        visualization.id,
    )
    settings_path = os.path.join(visualization_path, "settings.json")
    with open(settings_path, "r") as fs:
        settings = json.load(fs)
        if settings["has_entities"]:
            entities_path = os.path.join(visualization_path, "entities.json")
            if not os.path.exists(entities_path):
                return "Visualization found but could not find the entities file", 500

            with open(entities_path, "r") as fs:
                entities = json.load(fs)
        else:
            entities = []
    return jsonify({"Entities": entities})


@bp.route("/getVMapFileFromVisualization", methods=["POST"])
@login_required
def get_vmap_file_from_visualization():
    """
    :return:
    404 (NOT FOUND) if:
    # The entity file cannot be found.

    200 (OK) if the file exists, Returns an entity file with the requested dataset id
    """
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    if visualization is None:
        return "Could not found requested visualization", 400
    dataset_name = visualization.dataset
    if os.path.exists(os.path.join(current_app.config["DATASETS_ROOT"], dataset_name)):
        try:
            vmap_path = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name ,"VMap.csv")
            with open(vmap_path, "r") as fs:
                reader = csv.reader(fs)
                next(reader) 
                data_dict = {}
                for row in reader:
                    key = row[0]
                    value = row[1]
                    data_dict[key] = value
                return jsonify(data_dict)
        except FileNotFoundError:
            return jsonify({"message": "the current dataset file has no vmap file."}), 206
    else:
        return jsonify({"message": "the request VMap file cannot be found."}), 404


@bp.route("/getStates", methods=["POST"])
@login_required
@validate_args(["visualization"])
def get_states():
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    if visualization is None:
        return "Could not found requested visualization", 400

    negative = models.negative_karma_lego.query.filter_by(id=visualization.KL_id).first()
    if negative is not None:
        return "Negative Dataset", 200

    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        visualization.dataset,
        "visualizations",
        visualization.id,
        "states.json",
    )
    if not os.path.exists(path):
        return "Visualization found but could not find the states file", 500

    with open(path, "r") as fs:
        states_from_file = json.load(fs)
    return jsonify({"States": states_from_file})


@bp.route("/initiateTirps", methods=["POST"])
@login_required
@validate_args(["visualization"])
def initiate_tirps():
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    if visualization is None:
        return "Could not found requested visualization", 400
    
    negative =  models.negative_karma_lego.query.filter_by(id=visualization.KL_id).first()
    if negative is not None:
        root_path = os.path.join(
            current_app.config["DATASETS_ROOT"],
            visualization.dataset,
            negative.discretization_name,
            visualization.KL_id,
            "negative_output.json"
        )

        root = []
        with open(root_path, "r") as fr:
            lines = json.load(fr)
            for line in lines:
                root.append(line)

        response = make_response(jsonify(root))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    else:
        root_path = os.path.join(
            current_app.config["DATASETS_ROOT"],
            visualization.dataset,
            "visualizations",
            visualization.id,
            "chunks",
            "root.json",
        )

        if not os.path.exists(root_path):
            return "Visualization found but could not find the root file", 500

        visualization_path = os.path.join(
            current_app.config["DATASETS_ROOT"],
            visualization.dataset,
            "visualizations",
            visualization.id,
        )
        states, _ = ParseOutputFile.parse_states_file(visualization_path)
        root = []
        with open(root_path, "r") as fr:
            lines = json.load(fr)
            for line in lines:
                tirp_ob = tirp(None, None, None)
                tirp_ob.from_json(line)
                root.append(tirp_ob.to_old_tirp(states).__dict__)

        response = make_response(jsonify({"Root": root}))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response


@bp.route("/getSubTree", methods=["POST"])
@login_required
@validate_args(["visualization", "TIRP"])
def get_sub_tree():
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    if visualization is None:
        return "Could not found requested visualization", 400

    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        visualization.dataset,
        "visualizations",
        visualization.id,
    )

    TIRP_from_req = request.form["TIRP"]
    states, states_by_name = ParseOutputFile.parse_states_file(path)

    file_name = states_by_name[TIRP_from_req] + ".json"
    if os.path.isfile(path + "/chunks/" + file_name):
        with open(path + "/chunks/" + file_name, "r") as fr:
            tirp_json = json.load(fr)
            tirp_ob = tirp(None, None, None)
            tirp_ob.from_json(tirp_json)

    tirp_as_str = json.dumps(tirp_ob.to_old_tirp(states), default=lambda o: o.__dict__)
    tirp_as_dicts = json.loads(tirp_as_str)

    response = make_response(jsonify({"TIRPs": tirp_as_dicts}))
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@bp.route("/searchTirps", methods=["POST"])
@login_required
@validate_args(["visualization", "search_in_class_1", "startsList", "containList", "endsList"])
def searchTirps():
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    if visualization is None:
        return "Could not found requested visualization", 400

    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        visualization.dataset,
        "visualizations",
        visualization.id,
    )

    search_in_class_1 = bool(request.form["search_in_class_1"])
    startsList = (
        request.form["startsList"].split(",")
        if len(request.form["startsList"]) > 0
        else request.form["startsList"]
    )
    containList = (
        request.form["containList"].split(",")
        if len(request.form["containList"]) > 0
        else request.form["containList"]
    )
    endsList = (
        request.form["endsList"].split(",")
        if len(request.form["endsList"]) > 0
        else request.form["endsList"]
    )
    results_set = set()

    if search_in_class_1:
        minHS0 = int(request.form["minHS0"])
        maxHS0 = int(request.form["maxHS0"])
        minVS0 = int(request.form["minVS0"])
        maxVS0 = int(request.form["maxVS0"])
        minHS1 = int(request.form["minHS1"])
        maxHS1 = int(request.form["maxHS1"])
        minVS1 = int(request.form["minVS1"])
        maxVS1 = int(request.form["maxVS1"])
        need_to_filter_start = request.form["needToFilterStart"] == "true"
        need_to_filter_contains = request.form["needToFilterContains"] == "true"
        need_to_filter_end = request.form["needToFilterEnd"] == "true"

        searcher = SearchInIndexFile(path + "/search_index_class0")
        results = searcher.get_serached_tirps(
            start_sym=startsList,
            contains_sym=containList,
            end_sym=endsList,
            min_m_hs=minHS0,
            max_m_hs=maxHS0,
            min_vs=minVS0,
            max_vs=maxVS0,
            need_to_filter_start=need_to_filter_start,
            need_to_filter_contains=need_to_filter_contains,
            need_to_filter_end=need_to_filter_end,
        )
        searcher_class_1 = SearchInIndexFile(path + "/search_index_class1")
        results_class_1 = searcher_class_1.get_serached_tirps(
            start_sym=startsList,
            contains_sym=containList,
            end_sym=endsList,
            min_m_hs=minHS1,
            max_m_hs=maxHS1,
            min_vs=minVS1,
            max_vs=maxVS1,
            need_to_filter_start=need_to_filter_start,
            need_to_filter_contains=need_to_filter_contains,
            need_to_filter_end=need_to_filter_end,
        )
        # every tirp contains unique id number, we cut it to compare the tirps
        results_0_without_ids = list(map(lambda tirp: tirp.split(",")[:-1], results))
        results_1_without_ids = list(map(lambda tirp: tirp.split(",")[:-1], results_class_1))
        merged_results = []
        for result in results_0_without_ids:
            if result in results_1_without_ids:
                merged_results.append(",".join(result))
        response = make_response(jsonify({"Results": merged_results}))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    # need to search only in class 0 -----------------------------------------------------------------------------
    else:
        minHS = int(request.form["minHS"])
        maxHS = int(request.form["maxHS"])
        minVS = int(request.form["minVS"])
        maxVS = int(request.form["maxVS"])
        need_to_filter_start = request.form["needToFilterStart"] == "true"
        need_to_filter_contains = request.form["needToFilterContains"] == "true"
        need_to_filter_end = request.form["needToFilterEnd"] == "true"

        searcher = SearchInIndexFile(path + "/search_index_class0")
        results = searcher.get_serached_tirps(
            start_sym=startsList,
            contains_sym=containList,
            end_sym=endsList,
            min_m_hs=minHS,
            max_m_hs=maxHS,
            min_vs=minVS,
            max_vs=maxVS,
            need_to_filter_start=need_to_filter_start,
            need_to_filter_contains=need_to_filter_contains,
            need_to_filter_end=need_to_filter_end,
        )
        for result in results:
            result_arr = result.split(",")
            results_set.add(result_arr[0] + result_arr[1])

    response = make_response(jsonify({"Results": results}))
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@bp.route("/find_Path_of_tirps", methods=["POST"])
@login_required
@validate_args(["visualization"])
def find_Path_of_tirps():
    visualization = models.Visualization.query.filter_by(id=request.form["visualization"]).first()
    if visualization is None:
        return "Could not found requested visualization", 400

    path = os.path.join(
        current_app.config["DATASETS_ROOT"],
        visualization.dataset,
        "visualizations",
        visualization.id,
    )

    json_path_of_tirps = []
    states, states_by_name = ParseOutputFile.parse_states_file(path)
    symbols = request.form["symbols"]
    relations = request.form["relations"]
    if "to_add_entities" in request.form:
        to_add_entities = request.form["to_add_entities"]
    else:
        to_add_entities = None
    path_of_tirps = Index.find_Path_of_tirps(
        symbols=symbols,
        rels=relations,
        data_set_path=path,
        states=states,
        states_by_name=states_by_name,
        to_add_entities=to_add_entities,
    )
    for tirp in path_of_tirps:
        json_path_of_tirps.append(json.dumps(tirp, default=lambda x: x.__dict__))
    response = make_response(jsonify({"Path": json_path_of_tirps}))
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
