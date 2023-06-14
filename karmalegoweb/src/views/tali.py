from flask import Blueprint, request
from karmalegoweb.src.Visualization.Tali import api

bp = Blueprint("tali", __name__, "/")

# ########################################################################################################################################################################
# Tali's server
###################################################################################################################################################################################


def call_tali_preprocess(visualization_id, dataset_name):
    api.initialize(dataset_name=dataset_name, visualization_path=visualization_id)


@bp.route("/initialize_tali", methods=["POST"])
def set_dataset_name():
    visualization_id = request.args["visualization_id"]
    dataset_name = request.args["datasetName"]
    call_tali_preprocess(visualization_id=visualization_id, dataset_name=dataset_name)
    return ""  # every route method has to return something"


@bp.route("/get_symbol_TIRPs")
def get_symbol_TIRPs():
    visualization_id = request.args["visualization_id"]
    dataset_name = request.args["datasetName"]
    return api.get_symbol_TIRPs(dataset_name=dataset_name, visualization_path=visualization_id)


@bp.route("/tirpsJson")
def get_tirps_json():
    visualization_id = request.args["visualization_id"]
    dataset_name = request.args["datasetName"]
    return api.get_tirps_json(dataset_name=dataset_name, visualization_path=visualization_id)

@bp.route("/correlatedSymbols")
def get_correlated_symbols():
    visualization_id = request.args["visualization_id"]
    dataset_name = request.args["datasetName"]
    return api.get_correlated_symbols(dataset_name=dataset_name, visualization_path=visualization_id)

@bp.route("/symbols_to_names")
def get_symbols_names():
    visualization_id = request.args["visualization_id"]
    dataset_name = request.args["datasetName"]
    return api.get_symbols_names(dataset_name=dataset_name, visualization_path=visualization_id)


@bp.route("/rawData")
def get_raw_data():
    # global api
    dataset_name = request.args["datasetName"]
    id_number = request.args["id_number"]
    return api.get_raw_data(dataset_name=dataset_name, id_number=id_number)


@bp.route("/symbols_values_data")
def get_values_data():
    # global api
    dataset_name = request.args["datasetName"]
    visualizationid = request.args["visualizationId"]
    return api.get_symbols_values_data(dataset_name=dataset_name, visualizationid = visualizationid)


@bp.route("/get_more_raw_data")  # raw data loading
def load_more_entities():
    # global api
    # return api.get_more_raw_data()
    return ""

@bp.route("/supporting")  # raw data loading
def get_supporting():
    # global api
    # return api.get_more_raw_data()
    tirp_name = request.args["tirp_name"]
    visualizationid = request.args["visualizationId"]
    dataset_name = request.args["datasetName"]
    print("--")
    return api.get_supporting(tirp_name=tirp_name, dataset_name=dataset_name, visualizationid = visualizationid)


@bp.route("/descriteData")
def get_descrite_data():
    dataset_name = request.args["datasetName"]
    id_number = request.args["id_number"]
    visualizationid = request.args["visualizationId"]
    return api.get_descrite_data(dataset_name=dataset_name, id_number=id_number, visualizationid=visualizationid)


@bp.route("/get_more_descrite_data")  # descrite data loading
def get_more_descrite_data():
    # global api
    # return api.get_more_descrite_data()
    return ""


@bp.route("/get_descritization_method")  # descrite data loading
def get_descritization_method():
    # global api
    # return api.get_descritization_method()
    return ""
