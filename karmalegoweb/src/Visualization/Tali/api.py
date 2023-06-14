import ast
from flask import current_app, g
from karmalegoweb.src.Visualization.Tali import Create_Indexes
from karmalegoweb.src.Visualization.Tali import Read_KL_Output_File
from karmalegoweb.src.Visualization.Tali.DescriteData import DescriteData
from karmalegoweb.src.Visualization.Tali.RawData import RawData
from karmalegoweb.src import tasks


import json
import os
COUNTER_FOR_LOAD = "0"
TIRPS_INDEX_FILE = "TIRPs_index.json"
SYMBOL_TIRPS = "symbol_TIRPs"
PROPERTIES = "properties_TIRPs.json"
RAW_DATA_INDEX = "raw_data_index"
DESCRITE_DATA_INDEX = "descrite_data_index"
TIRPS_JSON = "TIRPs_json.json"
RAW_DATA = RawData()
DESCRITE_DATA = DescriteData()


# my main class, it literally does everything!
# 	- initializes all the classes the project uses
# 	- checks if there are indexes that already exist for caching data and efficiency
# 	- if there is no index - first run ever, then created TIRPs, relation vectors indexes
# 	- if there are such indexes, load their data and store it as class attributes


def initialize(dataset_name, visualization_path):
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "Visualizations", visualization_path
    )
    tirps_path = os.path.join(dataset_path, "Tali", TIRPS_INDEX_FILE)
    symbol_tirps_path = os.path.join(dataset_path, "Tali", SYMBOL_TIRPS)
    tirps_json_path = os.path.join(dataset_path, "Tali", TIRPS_JSON)
    # properties_path = os.path.join(dataset_path, "Tali", PROPERTIES)
    # if at least one of the paths does not exist, create it using Read_KL_Output_File.initialize_read_file
    if (
        not os.path.exists(tirps_path)
        or not os.path.exists(symbol_tirps_path)
        or not os.path.exists(tirps_json_path)
    ):
        symbol_TIRPs, symbols_to_names = Read_KL_Output_File.initialize_read_file(
            visualization_path=dataset_path
        )
        # serializing to index files, the return value is not interesting
        # tirps = Create_Indexes.create_TIRPs_index(visualization_path=dataset_path, tirps=tirps)
        symbol_TIRPs = Create_Indexes.create_symbol_TIRPs_index(
            visualization_path=dataset_path, symbol_TIRPs=symbol_TIRPs
        )
        current_app.logger.debug("TALI PREPROCESSING - index for symbol tirps")
        # tirps_json = Create_Indexes.create_TIRPs_json_index(
        #     visualization_path=dataset_path, tirps_json=tirps_json
        # )
        # correlated_symbols = Create_Indexes.create_correlation_json(
        #     visualization_path=dataset_path, correlation_symbols=correlated_symbols
        # )
        symbols_to_names = Create_Indexes.create_symbols_names_index(
            visualization_path=dataset_path, symbols_to_names=symbols_to_names
        )
        current_app.logger.debug("TALI PREPROCESSING - created index for symbols names")
        # create a file with name 'finished' as indication for later
        indicate_finished(visualization_path=dataset_path, dataset_name=dataset_name)
        try:
            tasks.send_email(
                message=f'Subject: A Symbol Exploration Visualization for Your dataset "'
                + dataset_name
                + '" has been successfully created',
                receiver_email=g.user.Email,
            )
        except:
            print("could not send email in Tali processing")


"""creates the file with the name 'finished' as indication for finished preprocessing"""


def indicate_finished(dataset_name, visualization_path):
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "Visualizations", visualization_path
    )
    path = os.path.join(dataset_path, "Tali", "finished")
    with open(path, "w") as file:
        file.write("finished")


def get_symbol_TIRPs(dataset_name, visualization_path):
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "Visualizations", visualization_path
    )
    symbol_TIRPs = Create_Indexes.create_symbol_TIRPs_index(
        visualization_path=dataset_path, symbol_TIRPs={}
    )
    return json.dumps(symbol_TIRPs)


def get_tirps_json(dataset_name, visualization_path):
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "Visualizations", visualization_path
    )
    tirps = Create_Indexes.create_TIRPs_json_index(visualization_path=dataset_path, tirps_json=[])
    return json.dumps(tirps)

def get_symbols_names(dataset_name, visualization_path):
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "Visualizations", visualization_path
    )
    symbols_names = Create_Indexes.create_symbols_names_index(visualization_path=dataset_path, symbols_to_names={})
    return json.dumps(symbols_names)

def get_correlated_symbols(dataset_name, visualization_path):
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "Visualizations", visualization_path
    )
    correlated_symbols = Create_Indexes.create_correlation_json(visualization_path=dataset_path, correlation_symbols={})
    return json.dumps(correlated_symbols)

def get_raw_data(dataset_name, id_number):
    # dataset_path = os.path.join(
    #     current_app.config["DATASETS_ROOT"], dataset_name, dataset_name
    # )
    global COUNTER_FOR_LOAD
    count = COUNTER_FOR_LOAD
    global RAW_DATA
    if count == "0":
        COUNTER_FOR_LOAD = "1"
        rawData = RawData.parse_raw_data(RAW_DATA,dataset_name,id_number)
        return json.dumps(rawData)
    else:
        COUNTER_FOR_LOAD = "1"
        rawData = RawData.load_more_raw_data(RAW_DATA,dataset_name,id_number)
        return json.dumps(rawData)
    # json_data = self.raw_class.get_raw_data(self.dataset_path)
    # return json_data


def get_more_raw_data(self):
    # json_data = self.raw_class.get_more_raw_data(self.dataset_path)
    # return json_data
    return ""

def get_supporting(tirp_name, visualizationid, dataset_name):
    print()
    name = tirp_name.split("|")[0].split("-")
    if (os.path.exists(os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "visualizations", visualizationid, "chunks_with_entities", name[0] + ".json"
    ))):
        path_to_tirp_entities = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "visualizations", visualizationid, "chunks_with_entities", name[0] + ".json"
        )
    else:
        return
    with open(path_to_tirp_entities) as file:
        entities = json.load(file)
        supporting = {}
        index = 0
        while entities["symbols"] != name:
            children = entities["children"]
            for k in range(len(children)):
                if children[k]["symbols"] == name[:index+1]:
                    entities = children[k]
            
            index +=1
        ent = list(map(lambda x : {"id":x,"name":x}, list(entities["stats_cls0"]["entities"].keys())))

        return json.dumps(ent)



def get_symbols_values_data(dataset_name, visualizationid):
    # json_data = self.raw_class.get_values_data(self.dataset_path)
    # return json_data
    if (os.path.exists(os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "visualizations", visualizationid, "Tali", "symbols_to_names.json"
    ))):
        path = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "visualizations", visualizationid, "Tali", "symbols_to_names.json"
        )
    else:
        return
    if (os.path.exists(os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "visualizations", visualizationid, "states.json"
    ))):
        path_to_temporal = os.path.join(
        current_app.config["DATASETS_ROOT"], dataset_name, "visualizations", visualizationid, "states.json"
        )
    else:
        return

    dct ={}
    name_symbol={}
    with open(path_to_temporal) as file:
        temporal = json.load(file)
    with open(path) as file:
        states = json.load(file)
        for i in states:
            name_symbol[states[i]] = i
    for i in temporal:
        dct[states[i["StateID"]]] = [i["TemporalPropertyID"],i["BinLow"],i["BinHigh"]]
    return {"state_temporal":dct, "name_symbol":name_symbol}


def get_descrite_data(dataset_name, id_number, visualizationid):
    global DESCRITE_DATA
    descriteData, range = DESCRITE_DATA.parse_descrite_data(dataset_name,id_number,visualizationid)
    return json.dumps({"descriteData":descriteData, "range":range})


def get_more_descrite_data(self):
    # json_data = self.raw_class.get_more_descrite_data(self.dataset_path)
    # return json_data
    return ""


def get_descritization_method(self):
    # json_data = self.raw_class.get_descritization_method(self.dataset_path)
    # return json_data
    return ""

def get_negative_data(dataset_name):
    directory = "negatives"
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], directory, dataset_name
    )
    with open(dataset_path, "r") as file:
        data = json.load(file)
        return json.dumps(data)
        

def get_negative_variables(dataset_name):
    directory = "negatives"
    dataset_path = os.path.join(
        current_app.config["DATASETS_ROOT"], directory ,dataset_name
    )
    with open(dataset_path, "r") as file:
        content = file.read()
        content = content[11:]
        dictionary = ast.literal_eval(content)
        return json.dumps(dictionary)
        

