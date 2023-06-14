from ast import Break
import pandas as pd
import json
from flask import current_app
import os

RAW_DATA_INDEX= "raw_data_index.json"
DESCRITE_DATA_INDEX = "descrite_data_index.json"
NAMES_TO_VALUES_INDEX = "names_to_values_index.json" # variable names and their cutoffs (low, medium, high)
ID_TO_NAMES_INDEX = "id_to_names_index.json" # temporal property id to it's name
ID_TO_VALUES_INDEX = "id_to_values_index.json" # temporal property id to it's information

NUM_ENTITIES_TO_LOAD_MORE = 10
STATES_FILE = "states.json"
DESCRITE_FILE = "KL.txt"

presented_entities_ids = [] # id for every entity that is presented in raw data screen - lazy loading


class RawData (object):

    def __init__(self):

        self.raw_json = {}
        self.descrite_json = {}
        self.descritization_method = None

        self.state_name_to_values_json = {}
        self.state_id_to_names_json = {}
        self.state_id_to_values_json = {}

        self.raw_index_to_load = 0
        self.descrite_index_to_load = 0


    """called the first time user asks for raw data, initialize the counter"""
    def parse_raw_data(self, dataset_name,id_number):
        self.raw_index_to_load = 0
        global presented_entities_ids
        presented_entities_ids = []
        return self.load_more_raw_data(dataset_name,id_number)


    """load 10 more entities with their descrite data"""
    def load_more_raw_data(self, dataset_name,id_number):
        import os
        from pathlib import Path
        parent = Path(__file__).parent.parent
        path = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\" + RAW_DATA_INDEX
        json_to_return = {}
        if os.path.exists(path):
            with open(path, "r") as file:
                raw_json = json.load(file)
        else:
            raw_json = self.create_raw_index(dataset_name,id_number)
        return raw_json
        new_entities_ids = list(raw_json.keys())[self.raw_index_to_load: self.raw_index_to_load + NUM_ENTITIES_TO_LOAD_MORE]
        global presented_entities_ids
        presented_entities_ids += new_entities_ids
        for entity_id in new_entities_ids:
            json_to_return[entity_id] = raw_json[entity_id]
        self.raw_index_to_load += NUM_ENTITIES_TO_LOAD_MORE
        return json_to_return


    """method is called the first time the user asks for descrite data"""
    def parse_descrite_data(self, dataset_name):
        self.descrite_index_to_load = 0
        return self.load_more_descrite_data(dataset_name)


    """method is called for loading descrite data for 10 new entities"""
    def load_more_descrite_data(self, dataset_name):
        import os
        from pathlib import Path
        parent = Path(__file__).parent.parent
        path = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\" + DESCRITE_DATA_INDEX
        json_to_return = {}
        if os.path.exists(path):
            with open(path, "r") as file:
                descrite_json = json.load(file)
        else:
            descrite_json = self.create_descrite_index(dataset_name)
        return descrite_json
        global presented_entities_ids
        entities_ids = presented_entities_ids
        for entity_id in entities_ids:
            json_to_return[entity_id] = descrite_json[entity_id]
        return json_to_return


    """method updates the json of symbol names to their bin values, if needed reads the info from the index file"""
    def set_json_states(self, dataset_name):
        from pathlib import Path
        parent = Path(__file__).parent.parent
        path = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali"
        with open(path + "\\"+NAMES_TO_VALUES_INDEX, "r") as file:
            names_to_values_index = json.load(file)
            self.state_name_to_values_json = names_to_values_index
            return self.state_name_to_values_json


    """creates index file for raw data of all entities in one json, and saves the info as a class field for later"""
    def create_raw_index(self, dataset_name,id_number):
        from pathlib import Path
        parent = Path(__file__).parent.parent
        path = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name) 
        try:
            path_csv = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name, dataset_name+".csv") # try to open csv file
            df = pd.read_csv(path_csv)
        except:
            path_xlsx = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name, dataset_name+".xlsx") # try to open xlsx file
            df = pd.read_excel(path_xlsx)
        raw_data_rows = df
        try:
            with open(path + "\\" +RAW_DATA_INDEX, "r") as file:
                pass
        except:
            with open(path + "\\" +RAW_DATA_INDEX, "w") as file:
                file.write(json.dumps())
        with open(path + "\\" +RAW_DATA_INDEX, "r") as file: # check if already gor data
            f= json.load(file)
            for i in f:
                if int(i) == int(id_number):
                    return {i:f[i]}
        with open(path + "\\" +RAW_DATA_INDEX, "w") as file:
            raw_json = self.prepare_raw_json_serialize(raw_data_rows, id_number) # get all data from raw data file
            self.raw_json = raw_json
            serialized_json = json.dumps(raw_json)
            a=json.loads(serialized_json)
            b=json.loads(json.dumps(f))
            c= dict(list(a.items()) + list(b.items()))
            file.write(json.dumps(c))
        return raw_json

    """helper function that gets all the entities raw data and returns a whole json that represents them all to serialize"""
    def prepare_raw_json_serialize(self, raw_data_rows,id_number):
        raw_json = {}
        #total_num_of_rows = raw_data_rows.shape[0]
        for row in raw_data_rows.itertuples():
            entity_id = int(row.EntityID)
            if (entity_id != int(id_number)):
                continue
            if (entity_id == int(id_number)):
                if raw_json.get(entity_id,-1) == -1 :
                    raw_json[entity_id] = {}
                json_of_entity = raw_json[entity_id]
                symbol = row.TemporalPropertyID
                time = row.TimeStamp
                value = row.TemporalPropertyValue
                if json_of_entity.get(symbol,-1) == -1:
                    json_of_entity[symbol] = [[int(time), float(value)]]
                else:
                    json_of_entity[symbol].append([int(time), float(value)])
                raw_json[entity_id] = json_of_entity
        return raw_json


    """created an index file for all the entities descrite data in a one big json, serializes it to the file"""
    def create_descrite_index(self, dataset_name):
        from pathlib import Path
        parent = Path(__file__).parent.parent
        path = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name) 
        path_descrite = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\"+DESCRITE_FILE
        descrite_file = open(path_descrite, "r")
        descrite_file.readline()  # for 'start toncetps'
        descrite_file.readline()  # for 'number of entities'
        descrite_json = self.prepare_descrite_json_serialize(descrite_file)
        self.descrite_json = descrite_json
        with open(path, "w") as file:
            serialized_json = json.dumps(descrite_json, default=lambda o: o.__dict__, indent=4)
            file.write(serialized_json)
        return descrite_json

    """helper function, gets all the descrite data of all entities read from a file and returns a json representation of the data
    to be serialized to an index file"""
    def prepare_descrite_json_serialize(self, descrite_file):
        import re
        descrite_json = {}
        while True:
            line1 = descrite_file.readline()
            line2 = descrite_file.readline()
            if not line2:
                break  # EOF
            else:
                line1_components = re.split(',|;|\n|\'', line1)
                standard_mode = True if len(line1_components) == 5 else False  # Alisa's dataset in different standard
                entity_id_idx = 0 if standard_mode else 2
                entity_id = int(line1_components[entity_id_idx])
                if entity_id not in descrite_json:
                    descrite_json[entity_id] = {}
                json_of_entity = descrite_json[entity_id]
                intervals = line2.split(';')
                for interval in intervals:
                    interval_components = re.split(',|\n', interval)
                    if len(interval_components) < 4:  # the \n in the end of the row
                        break

                    temporal_property_id = str(int(interval_components[3]))
                    symbol_name = self.state_id_to_names_json.get(temporal_property_id)
                    if symbol_name is not None:
                        state_id = str(int(interval_components[2]))
                        start_time = int(interval_components[0])
                        end_time = int(interval_components[1])
                        value_label = self.state_id_to_values_json[state_id]['value']
                        if symbol_name not in json_of_entity:
                            json_of_entity[symbol_name] = [[start_time, end_time, value_label]]
                        else:
                            json_of_entity[symbol_name].append([start_time, end_time, value_label])
                descrite_json[entity_id] = json_of_entity
        return descrite_json


    """created 3 index files, one for every needed purpose:
    NAMES_TO_VALUES_INDEX - index file that for every variable name there is it's values (low,medium,high) of the bins
    ID_TO_NAMES_INDEX - index file that for every variable ID there is it's name  for example ID:733 to 'heartRate.low'
    ID_TO_VALUES_INDEX - index file that for every variable ID there is it's value  for example ID:733 to (low,medium,high) of the bins'"""
    def create_states_values_index(self, dataset_name):
        from pathlib import Path
        import os
        parent = Path(__file__).parent.parent
        path = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\"+STATES_FILE
        path_name_to_values = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\"+NAMES_TO_VALUES_INDEX
        path_ids_to_names = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\"+ID_TO_NAMES_INDEX
        path_ids_to_values = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\"+ID_TO_VALUES_INDEX

        if os.path.exists(path_name_to_values) and os.path.exists(path_ids_to_names) and os.path.exists(path_ids_to_values):
            return self.deserialize_states(dataset_name)

        state_name_to_values_json, state_id_to_values_json, state_id_to_names_json = self.prepare_symbols_values_serialize(path)

        self.state_name_to_values_json = state_name_to_values_json
        self.state_id_to_names_json = state_id_to_names_json
        self.state_id_to_values_json = state_id_to_values_json

        path = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali"
        with open(path+"\\"+NAMES_TO_VALUES_INDEX, "w") as file:
            serialized_json = json.dumps(state_name_to_values_json, default=lambda o: o.__dict__, indent=4)
            file.write(serialized_json)
        with open(path+"\\"+ID_TO_NAMES_INDEX, "w") as file:
            serialized_json = json.dumps(state_id_to_names_json, default=lambda o: o.__dict__, indent=4)
            file.write(serialized_json)
        with open(path+"\\"+ID_TO_VALUES_INDEX, "w") as file:
            serialized_json = json.dumps(state_id_to_values_json, default=lambda o: o.__dict__, indent=4)
            file.write(serialized_json)

        return self.state_name_to_values_json


    """gets the path of the file to read and returns a json representation to serialize to 3 different index files"""
    def prepare_symbols_values_serialize(self, path):
        from numpy import inf
        max_bin = 0
        state_name_to_values_json = {}
        state_id_to_values_json = {}
        temporal_id_to_names_json = {}
        with open(path) as jsonFile:
            import json
            for row in jsonFile:
                a = json.loads(row)
                # self.descritization_method = a['Method']
                state_id = a['StateID']
                temporal_property_id = a['TemporalPropertyID']
                try:
                    temporal_property_name = a["TemporalPropertyName"]
                except:
                    temporal_property_name = temporal_property_id
                try:
                    label = a['BinLabel']
                except:
                    label = a['BinID']
                    if int(label) > max_bin:
                        max_bin = int(label)
                if a['BinLow'] == "#NAME?" or a['BinLow'] == "-inf":
                    low_value = str(-inf)
                else: # BinLow is numeric
                    low_value = float(a['BinLow'])

                if a['BinHigh'] == "inf":
                    high_value = str(inf)
                else: # BinHigh is numeric
                    high_value = float(a['BinHigh'])

                state_id_to_values_json[state_id] = {
                    'TemporalPropertyID': temporal_property_id,
                    'TemporalPropertyName': temporal_property_name,
                    'value': label
                }

                if temporal_property_id not in temporal_id_to_names_json:
                    temporal_id_to_names_json[temporal_property_id] = temporal_property_name

                if temporal_property_name not in state_name_to_values_json:
                    state_name_to_values_json[temporal_property_name] = {label: [low_value, high_value]}
                else:
                    state_name_to_values_json[temporal_property_name][label] = [low_value, high_value]

            if max_bin > 0: #no labels in states file (only bin numbers)
                if max_bin == 2:
                    labels_dict = {'0': 'Low', '1':'Medium', '2':'High'}
                if max_bin == 1:
                    labels_dict = {'0': 'low', '1':'high'}
                for state_id in state_id_to_values_json:
                    state_json = state_id_to_values_json[state_id]
                    bin_label = state_json['value']
                    state_id_to_values_json[state_id]['value'] = labels_dict[bin_label]
                new_state_name_to_values_json = {} # return new dict when the values are strings rather than bin values
                # python can not change keys in dict dynamically so create a new dict
                for temporal_name in state_name_to_values_json:
                    new_state_name_to_values_json[temporal_name] = {}
                    values = state_name_to_values_json[temporal_name]
                    for value in values:
                        new_state_name_to_values_json[temporal_name][labels_dict[value]] = state_name_to_values_json[temporal_name][value]
                state_name_to_values_json = new_state_name_to_values_json

        return state_name_to_values_json, state_id_to_values_json, temporal_id_to_names_json


    """reads the 3 index files of the states and returns their jsons representations and saves them as class fieidls"""
    def deserialize_states(self, dataset_name):

        from pathlib import Path
        parent = Path(__file__).parent.parent
        path = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali\\"

        """first checking if the data already computed, only if not then load it from the index files"""
        if self.state_name_to_values_json == {}:
            with open(path + "\\"+NAMES_TO_VALUES_INDEX, "r") as file:
                names_to_values_index = json.load(file)
                self.state_name_to_values_json = names_to_values_index
        if self.state_id_to_names_json == {}:
            with open(path + "\\"+ID_TO_NAMES_INDEX, "r") as file:
                id_no_names_index = json.load(file)
                self.state_id_to_names_json = id_no_names_index
        if self.state_id_to_values_json == {}:
            with open(path + "\\"+ID_TO_VALUES_INDEX, "r") as file:
                id_to_values_index = json.load(file)
                self.state_id_to_values_json = id_to_values_index

        return self.state_name_to_values_json


    """when the user wants to know the descritization method for the current dataset, return it if exists as class fields, else
    it is enough to read the first line only in 'states.json' file ans return it's method
    (every line in this file contains the same method so it's enough to look at the first one only)"""
    def load_descritization_method(self, dataset_name):
        # if self.descritization_method != None:
        #     return self.descritization_method
        # else:
        #     from pathlib import Path
        #     parent = Path(__file__).parent.parent
        #     path = str(parent.absolute()) + "\\DataSets" + dataset_name + "\\Tali"
        #     with open(path + "\\"+STATES_FILE, "r") as jsonFile:
        #         for row in jsonFile:
        #             a = json.loads(row)
        #             self.descritization_method = a['Method']
        #             return self.descritization_method
        return None


    """section of getters functions that are called from the Tali\\api.py class"""
    def get_raw_data(self, path):
        return self.parse_raw_data(path)

    def get_more_raw_data(self, path):
        return self.load_more_raw_data(path)

    def get_values_data(self, path):
        return self.create_states_values_index(path)

    def get_descrite_data(self, path):
        return self.parse_descrite_data(path)

    def get_more_descrite_data(self, path):
        return self.load_more_descrite_data(path)

    def get_descritization_method(self, dataset_name):
        return self.load_descritization_method(dataset_name)
