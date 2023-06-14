from karmalegoweb.src.Visualization.Tali import TIRP
import re
import json
import os.path
from os import path
from flask import current_app


"""this method is taken from Guy's code"""


def get_supporting_instances(entities, instances, line_vector, symbols, index, next_line, entities_stats={}):
    import re
    import sys
    from karmalegoweb.src.Visualization.SymbolicTimeInterval import SymbolicTimeInterval
    from karmalegoweb.src.Visualization.SupportingInstance import SupportingInstance

    next_line_parsed = re.split("[ \[ , \]]", next_line)
    line = line_vector[index + 8 :]
    for word in range(0, len(line) - 4, 5):
        hs_count = 0
        entity_id = line[word]
        instance_vec = []
        symbolic_list = []
        tis = list(filter(None, line[word + 1].split("]")))
        for t in range(0, len(tis)):
            times = tis[t].split("-")
            start_time = int(times[0].replace("[", ""))
            end_time = int(times[1])
            if start_time == end_time:
                sys.exit("Error! Start time can't be equal to end time! please change KLC code")
            symbolic = SymbolicTimeInterval(
                start_time=start_time, end_time=end_time, symbol=symbols[t]
            )  # , duration=tis[t+1], offset_from_start=tis[t+2], offset_from_end=tis[t+3])
            symbolic_list.append(symbolic)
        instance_vec.append(symbolic_list)
        if entity_id in entities:
            instances[len(instances) - 1].add_list_to_intervals(instance_vec)
            entities_stats[entity_id][0] += 1
        else:
            if len(instances) > 0:
                instances[len(instances) - 1].set_means()
            for i in range(0, len(next_line_parsed) - 9, 11):
                if entity_id == next_line_parsed[i]:
                    mean_duration = float(next_line_parsed[i + 7])
                    mean_offset_from_start = float(next_line_parsed[i + 8])
                    mean_offset_from_end = float(next_line_parsed[i + 9])
                    break
            support_instance = SupportingInstance(
                entityId=str(entity_id),
                symbolic_intervals=instance_vec,
                mean_duration=mean_duration,
                mean_offset_from_start=mean_offset_from_start,
                mean_offset_from_end=mean_offset_from_end,
            )
            instances.append(support_instance)
            entities.append(entity_id)
            entities_stats[entity_id] = [1, mean_duration]
    instance_vec.clear()


"""this method gets a visualization path and initializes all data structures"""
def initialize_read_file(visualization_path):
    calc_offsets_class0 = False
    calc_offsets_class1 = False
    """saving the lines read from the file to later create the TIRPS"""
    class0_lines, calc_offsets_class0 = get_lines_from_file(visualization_path, "KLOutput_class0")
    class1_path = os.path.join(visualization_path, "KLOutput_class1")
    if path.exists(class1_path):  # read lines from class 1 only if exists
        class1_lines, calc_offsets_class1 = get_lines_from_file(
            visualization_path, "KLOutput_class1"
        )
    else:
        class1_lines = None

    """CONSTANTS"""
    TIRP_SIZE_0 = 0
    SYMBOLS_0 = 1
    RELATIONS_0 = 2
    NUM_SUPPORT_ENTITIES_0 = 3 if not calc_offsets_class0 else 6
    MEAN_HORIZONTAL_SUPPORT_0 = 4 if not calc_offsets_class0 else 7
    OCCURRENCES_0 = 5 if not calc_offsets_class0 else 8
    """class 1 constants"""
    TIRP_SIZE_1 = 0
    SYMBOLS_1 = 1
    RELATIONS_1 = 2
    NUM_SUPPORT_ENTITIES_1 = 3 if not calc_offsets_class1 else 6
    MEAN_HORIZONTAL_SUPPORT_1 = 4 if not calc_offsets_class1 else 7
    OCCURRENCES_1 = 5 if not calc_offsets_class1 else 8

    discovered_tirps = {}
    entities_properties, properties = parse_entities_file(visualization_path)
    """reading class 0 tirps and turns them into objects"""
    tirps = create_tirps(
        output_lines=class0_lines,
        tirp_size_idx=TIRP_SIZE_0,
        symbols_idx=SYMBOLS_0,
        relations_idx=RELATIONS_0,
        properties=properties,
        entities_properties=entities_properties,
        num_sup_ent_idx=NUM_SUPPORT_ENTITIES_0,
        discovered_tirps=discovered_tirps,
        tirps_list=[],
    )
    current_app.logger.debug("TALI PREPROCESSING - created tirps class 0")
    """reading class 1 tirps and turns them into objects"""
    if class1_lines != None:
        tirps = create_tirps(
            output_lines=class1_lines,
            tirp_size_idx=TIRP_SIZE_1,
            symbols_idx=SYMBOLS_1,
            relations_idx=RELATIONS_1,
            num_sup_ent_idx=NUM_SUPPORT_ENTITIES_1,
            properties=properties,
            entities_properties=entities_properties,
            discovered_tirps=discovered_tirps,
            is_class_1=True,
            tirps_list=tirps,
        )
        current_app.logger.debug("TALI PREPROCESSING - created tirps class 1")
    """adding to every TIRP symbols their names"""
    symbols_to_names = set_tirps_names(visualization_path=visualization_path, tirps=tirps)
    """creating data structure of symbol tirps"""
    symbol_TIRPs = create_symbol_TIRPs(tirps=tirps)
    current_app.logger.debug("TALI PREPROCESSING - created symbol tirps")
    """creating data structure of tirp json"""
    # tirps_json = tirps_list_to_json(tirps_list=tirps)
    # correlated_symbols = create_symbols_correlation(tirps)
    # return tirps, symbol_TIRPs, tirps_json, correlated_symbols
    return symbol_TIRPs, symbols_to_names


"""gets path to KL output and returns all lines"""


def get_lines_from_file(visualization_path, class_path):
    path = os.path.join(visualization_path, class_path)
    myfile = open(path)
    lines = []
    for line in myfile:
        lines.append(line.rstrip("\n"))

    # first line is just karma-lego output parameters
    first_line = lines[0]
    all_params = re.split(";", first_line)
    params = list(map(lambda param_line: param_line.split("="), all_params))
    # there is a difference in the output of KL due to the 'calc offsets' parameter
    calc_offsets_class = False
    for parameter in params:
        if parameter[0] == "calc_offsets" and parameter[1] == "True":
            calc_offsets_class = True

    # actual output lines, and parameter calc_offsets
    return lines[1:], calc_offsets_class


"""gets the tirp objects and returns data structure of symbol tirps: 
    symbol4: {next: {
                    symbol2: [tirp1, tirp2, ...]
                    symbol3: [tirp7, tirp19, ...]
                    }
            prefix: {
                    symbol6: [tirp8, turp18, ...]
                    symbol15: [tirp3, tirp20, ...]
                    }
            }
    symbol8: {next: {
                    symbol12: [tirp11, tirp2, ...]
                    symbol43: [tirp27, tirp19, ...]
                    }
            prefix: {
                    symbol6: [tirp8, turp18, ...]
                    symbol15: [tirp3, tirp20, ...]
                    }
            }
    
    explanation: for every symbol(i), index all symbols(k) that can come after it as 'next symbols' and for each such symbol
    all tirps that contain the order symbol(i), symbol(k)
    same as for symbols that come before
            """


def create_symbol_TIRPs(tirps):
    symbols_connections_tirps = {}
    for tirp in tirps:
        tirp_symbols = tirp.get_symbols()
        matrix_column = tirp_symbols[:-1]
        matrix_row = tirp_symbols[1:]

        """in case this is a TIRP in size 1 (only one symbol), update the dictionary that prefix and next are None"""
        if matrix_column == [] and matrix_row == []:
            symbol = tirp_symbols[0]  # the only symbol
            if symbol not in symbols_connections_tirps:
                symbols_connections_tirps[symbol] = {
                    "next": {None: [tirp]},
                    "prefix": {None: [tirp]},
                }
            else:
                symbols_connections = symbols_connections_tirps[symbol]
                if "next" not in symbols_connections:
                    symbols_connections["next"] = {None: [tirp]}
                else:
                    symbols_connections["next"][None] = [tirp]
                if "prefix" not in symbols_connections:
                    symbols_connections["prefix"] = {None: [tirp]}
                else:
                    symbols_connections["prefix"][None] = [tirp]

        """in case there are more than 1 symbol in the current TIRP
            B   C   D
        A
        B
        C
        
        notations: column is [A,B,C], row is: [B,C,D]
        """
        for i in range(len(matrix_column)):
            symbol_column = matrix_column[i]
            if symbol_column not in symbols_connections_tirps:  # first time runnning in this symbol
                next_symbol_tirps = {}  # construct it's next json
                symbol_row = matrix_row[i]
                next_symbol_tirps[symbol_row] = [tirp]
                # for every column symbol, its immediate next is the one in the same index in row
                symbols_connections_tirps[symbol_column] = {"next": next_symbol_tirps}

            else:  # symbol already was in the connection json
                symbols_json = symbols_connections_tirps[symbol_column]
                if "next" in symbols_json:  # symbol already has it's next symbols
                    next_symbol_tirps = symbols_connections_tirps[symbol_column]["next"]
                    symbol_row = matrix_row[i]
                    if symbol_row not in next_symbol_tirps:
                        next_symbol_tirps[symbol_row] = [tirp]
                    else:
                        next_symbol_tirps[symbol_row].append(tirp)
                    symbols_connections_tirps[symbol_column][
                        "next"
                    ] = next_symbol_tirps  # updating after add

                else:  # maybe the symbol has no next symbols yet
                    next_symbol_tirps = {}
                    symbol_row = matrix_row[i]
                    next_symbol_tirps[symbol_row] = [tirp]
                    symbols_json[
                        "next"
                    ] = next_symbol_tirps  # adding the next json to the connected json
                    symbols_connections_tirps[symbol_column] = symbols_json  # updating after add

        for i in range(
            len(matrix_row)
        ):  # same process only for each row symbol we add all the symbols in the column as prefix
            symbol_row = matrix_row[i]
            if symbol_row not in symbols_connections_tirps:  # first time running in this symbol
                prefix_symbol_tirps = {}
                symbol_column = matrix_column[i]
                prefix_symbol_tirps[symbol_column] = [tirp]
                # for every row symbol, its immediate previous is the one in the same index in column
                symbols_connections_tirps[symbol_row] = {"prefix": prefix_symbol_tirps}

            else:  # symbol was already in the connected json
                symbols_json = symbols_connections_tirps[symbol_row]
                if "prefix" in symbols_json:  # symbol already has it's prefix symbols
                    prefix_symbol_tirps = symbols_connections_tirps[symbol_row]["prefix"]
                    symbol_column = matrix_column[i]
                    if symbol_column not in prefix_symbol_tirps:
                        prefix_symbol_tirps[symbol_column] = [tirp]
                    else:
                        prefix_symbol_tirps[symbol_column].append(tirp)
                    symbols_connections_tirps[symbol_row]["prefix"] = prefix_symbol_tirps

                else:  # maybe the symbol has no prefix symbols yet
                    prefix_symbol_tirps = {}
                    symbol_column = matrix_column[i]
                    prefix_symbol_tirps[symbol_column] = [tirp]
                    symbols_json[
                        "prefix"
                    ] = prefix_symbol_tirps  # adding the prefix json to the connected json
                    symbols_connections_tirps[symbol_row] = symbols_json

    return symbols_connections_tirps


"""gets the lines that were read from the file and creates corresponding TIRP objects"""


def create_tirps(
    output_lines,
    tirp_size_idx,
    symbols_idx,
    relations_idx,
    num_sup_ent_idx,
    entities_properties,
    properties,
    discovered_tirps,
    is_class_1=False,
    tirps_list=[],
):
    tirp_list = tirps_list
    lines_size = len(output_lines)
    for line_index in range(0, lines_size, 2):
        first_line = output_lines[line_index]
        first_line_vector = first_line.split(" ")

        line_vector = output_lines[line_index].split()
        next_line = output_lines[line_index + 1]

        size = int(first_line_vector[tirp_size_idx])

        # take the symbols only(last place is '' after split)
        symbols = first_line_vector[symbols_idx].split("-")[0:-1]
        # take the relations only(last place is '' after split)
        relations = first_line_vector[relations_idx].split(".")[0:-1]
        num_support_entities = first_line_vector[num_sup_ent_idx]

        if size > 1:
            index = 0
        else:
            index = -1

        mean_duration = float(line_vector[index + 3])
        mean_offset_from_start = float(line_vector[index + 4])
        mean_offset_from_end = float(line_vector[index + 5])
        vertical_support = int(line_vector[index + 6])
        mean_horizontal_support = float(line_vector[index + 7])
        entities = list()
        instances = []
        # this is a mutable method, changes <instances>
        entities_stats = {}
        get_supporting_instances(
            entities, instances, line_vector, symbols, index=index, next_line=next_line, entities_stats=entities_stats
        )
        if len(list(entities_properties.keys())) == 0:
            supporting_entities_properties = {}
        else:
            supporting_entities_properties = {
                entity_id: entities_properties[entity_id] for entity_id in entities
            }
        discovered_tirp = is_TIRP_already_discovered(
            tirp_symbols=symbols, tirp_relations=relations, discovered_tirps=discovered_tirps
        )
        if is_class_1:  # two class dataset and we scan not the class 1 tirps
            if discovered_tirp is not None:  # tirp already exist in class 0
                discovered_tirp.set_class_1_properties(
                    size=size,
                    symbols=symbols,
                    relations=relations,
                    num_supporting_entities=num_support_entities,
                    mean_horizontal_support=mean_horizontal_support,
                    supporting_entities_properties=supporting_entities_properties,
                    supporting_instances=instances,
                    mean_of_first_interval=0.0,
                    vertical_support=vertical_support,
                    mean_duration=mean_duration,
                    mean_offset_from_first_symbol=list(),
                    build_supporting_instances=True,
                    mean_offset_from_start=mean_offset_from_start,
                    mean_offset_from_end=mean_offset_from_end,
                    entities_stats=entities_stats
                )
                discovered_tirp.set_tirp_in_class1()

            else:  # tirp has not already discovered - exist only in class 1
                new_class_1_tirp = TIRP.TIRP(is_class_0=False)
                new_class_1_tirp.set_tirp_in_class1()
                new_class_1_tirp.set_class_1_properties(
                    size=size,
                    symbols=symbols,
                    relations=relations,
                    num_supporting_entities=num_support_entities,
                    mean_horizontal_support=mean_horizontal_support,
                    supporting_entities_properties=supporting_entities_properties,
                    supporting_instances=instances,
                    mean_of_first_interval=0.0,
                    vertical_support=vertical_support,
                    mean_duration=mean_duration,
                    mean_offset_from_first_symbol=list(),
                    build_supporting_instances=True,
                    mean_offset_from_start=mean_offset_from_start,
                    mean_offset_from_end=mean_offset_from_end,
                    entities_stats=entities_stats
                )
                tirp_list.append(new_class_1_tirp)
                if len(list(entities_properties.keys())) > 0:
                    for entity_id in entities:
                        entity_properties = list(entities_properties[entity_id].keys())
                        for prop in entity_properties:
                            if new_class_1_tirp not in properties[prop]:
                                properties[prop].append(new_class_1_tirp)
        else:  # we are scanning the class 0 file
            new_class_0_tirp = TIRP.TIRP(
                size=size,
                symbols=symbols,
                relations=relations,
                num_supporting_entities=num_support_entities,
                mean_horizontal_support=mean_horizontal_support,
                supporting_instances=instances,
                vertical_support=vertical_support,
                supporting_entities_properties=supporting_entities_properties,
                mean_duration=mean_duration,
                build_supporting_instances=True,
                is_class_0=True,
                mean_offset_from_start=mean_offset_from_start,
                mean_offset_from_end=mean_offset_from_end,
                entities_stats=entities_stats
            )
            new_class_0_tirp.set_tirp_in_class0()
            tirp_list.append(new_class_0_tirp)
            key = " ".join(symbols) + " ".join(relations)
            discovered_tirps[key] = new_class_0_tirp
            if len(list(entities_properties.keys())) > 0:
                for entity_id in entities:
                    entity_properties = list(entities_properties[entity_id].keys())
                    for prop in entity_properties:
                        if new_class_0_tirp not in properties[prop]:
                            properties[prop].append(new_class_0_tirp)

    return tirp_list


"""gets list of tirp objects and returns a json of corrleated symbols:
    {
        2: {
            3: {<: [4, 0], m: [2, 2]}
            4: {o: [2, 1]}
            }
        
    }
    this json contains as key: symbol and its value is json which its key is symbol and value is json
    which for each relation counts the number of TIRPs [class0, class1] this relation is among the two symbols
    """
def create_symbols_correlation(tirps):
    symbols_correlation = {}
    for tirp in tirps:
        tirp_symbols = tirp.get_symbols_names()
        matrix_column = tirp_symbols[:-1]
        matrix_row = tirp_symbols[1:]

        """in case there are more than 1 symbol in the current TIRP
            B   C   D
        A
        B
        C
        
        notations: column is [A,B,C], row is: [B,C,D]
        """
        for i in range(len(matrix_column)):
            symbol_column = matrix_column[i]
            if symbol_column not in symbols_correlation:  # first time runnning in this symbol
                symbols_correlation[symbol_column] = {}
            for j in range(len(matrix_row)):
                symbol_row = matrix_row[j]
                if symbol_row not in symbols_correlation[symbol_column]:
                    symbols_correlation[symbol_column][symbol_row] = {}
                # (i * (i + 1) / 2) - amount of `missing relations` in the half matrix
                i_j_relations_idx = int((len(tirp_symbols) - 1) * i - (i * (i + 1) / 2) + j)
                i_j_relation = tirp.get_relations()[i_j_relations_idx]
                if i_j_relation not in symbols_correlation[symbol_column][symbol_row]:
                    # first time for this relation in symbol_column,symbol_row
                    if tirp.is_in_class_0():
                        if tirp.is_in_class_1():
                            symbols_correlation[symbol_column][symbol_row][i_j_relation] = [1, 1]
                        else:
                            symbols_correlation[symbol_column][symbol_row][i_j_relation] = [1, 0]
                    else:
                        symbols_correlation[symbol_column][symbol_row][i_j_relation] = [0, 1]
                else:
                    # we already have seen this relation in symbol_column,symbol_row
                    class_0_count = symbols_correlation[symbol_column][symbol_row][i_j_relation][0]
                    class_1_count = symbols_correlation[symbol_column][symbol_row][i_j_relation][1]

                    if tirp.is_in_class_0():
                        if tirp.is_in_class_1():
                            symbols_correlation[symbol_column][symbol_row][i_j_relation] = [class_0_count+1, class_1_count+1]
                        else:
                            symbols_correlation[symbol_column][symbol_row][i_j_relation] = [class_0_count+1, class_1_count]
                    else:
                        symbols_correlation[symbol_column][symbol_row][i_j_relation] = [class_0_count, class_1_count+1]
    return symbols_correlation



def tirps_list_to_json(tirps_list):
    tirps_json = {}
    for tirp in tirps_list:
        tirp_unique_name = (
            tirp.string_symbols(tirp.get_symbols())
            + "-"
            + tirp.string_relations(tirp.get_relations())
        )
        tirps_json[tirp_unique_name] = tirp
    return tirps_json


"""searches in all the already discovered TIRPs for the cetrain TIPR by its unique name"""


def is_TIRP_already_discovered(tirp_symbols, tirp_relations, discovered_tirps):
    wanted_tirp = " ".join(tirp_symbols) + " ".join(tirp_relations)
    for key in discovered_tirps:
        if wanted_tirp == key:
            return discovered_tirps[key]
    return None


"""for every TIRP object adds its symbols names"""


def set_tirps_names(visualization_path, tirps):
    path = os.path.join(visualization_path, "states.json")
    symbols_to_names = {}
    with open(path) as jsonFile:
        states = json.load(jsonFile)
        for a in states:
            try:
                temporal_property_name = a["TemporalPropertyName"]
            except:
                temporal_property_name = a["TemporalPropertyID"]
            try:
                label = a["BinLabel"]
            except:
                label = a["BinID"]

            symbols_to_names[a["StateID"]] = temporal_property_name + "." + label
    for tirp in tirps:
        symbols_names = []
        for symbol in tirp.get_symbols():
            symbols_names.append(symbols_to_names[symbol])
        tirp.set_symbols_names(symbols_names)
    return symbols_to_names


"""reads the entities file and creates a json of all the properties of entities"""


def parse_entities_file(visualization_path):
    path = os.path.join(visualization_path, "entities.json")
    entities_properties = {}
    properties = {}
    if os.path.exists(path):
        with open(path) as jsonFile:
            rows = json.load(jsonFile)
            for a in rows:
                try:
                    entity_id = a["id"]
                except:
                    try:
                        entity_id = a["EntityID"]
                    except:
                        return {}, {}
                entities_properties[entity_id] = {}
                for key in a:
                    if key != "id":  # some property which isn't id
                        entities_properties[entity_id][key] = a[key]
                        if key not in properties:
                            properties[key] = []
    return entities_properties, properties
