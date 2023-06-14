import json
import os

from karmalegoweb.src.preprocessing.tirp import tirp
from karmalegoweb.src.Visualization.TIRP import TIRP


def find_Path_of_tirps(
    symbols, rels, data_set_path, states, states_by_name=None, to_add_entities=None
):
    relations_dict = {
        "<": "before",
        "m": "meets",
        "o": "overlaps",
        "f": "finished by",
        "c": "contains",
        "=": "equals",
        "s": "starts",
        "-": 7,
    }
    tirps_path = []
    rels = list(filter(None, rels.split(".")))
    symbols = list(filter(None, symbols.split("-")))

    if not to_add_entities:
        file_name = symbols[0] + ".json"
        dir_path = "/chunks/"

        for r in range(len(rels)):
            rels[r] = relations_dict[rels[r]]
        for i in range(len(symbols)):
            symbol = states[symbols[i]]
            symbols[i] = symbol
    else:
        file_name = states_by_name[symbols[0]] + ".json"
        dir_path = "/chunks_with_entities/"

    tirp_size = len(symbols)
    if os.path.isfile(data_set_path + dir_path + file_name):
        with open(data_set_path + dir_path + file_name, "r") as fr:
            tirp_dict = json.load(fr)
            tirp_obj = tirp(None, None, None)
            tirp_obj.from_json(tirp_dict)
            tirp_obj = tirp_obj.to_old_tirp(states)
            tirps_path.append(tirp_obj)
            if tirp_size > 1:
                childs = tirp_obj.get_childes()
                while len(tirps_path) < tirp_size:
                    for child in childs:
                        curr_tirp = TIRP()
                        curr_tirp.__dict__.clear()
                        curr_tirp.__dict__.update(child.__dict__)
                        curr_size = curr_tirp.get_tirp_size()
                        new_symbols = symbols[:curr_size]
                        num_of_new_rels = int(curr_size * (curr_size - 1) / 2)
                        new_rels = rels[:num_of_new_rels]
                        if curr_tirp.get_symbols() == new_symbols:
                            if curr_tirp.get_rels() == new_rels:
                                tirps_path.append(curr_tirp)
                                childs = curr_tirp.get_childes()
                                break
            return tirps_path
    else:
        with open(data_set_path + dir_path + "root.json", "r") as fr:
            roots_from_file = json.load(fr)
            for tirp_dict in roots_from_file:
                tirp_obj = TIRP()
                tirp_obj.__dict__.clear()
                tirp_obj.__dict__.update(tirp_dict)
                tirp_obj = tirp_obj.to_old_tirp(states)
                if tirp_obj.get_symbols() == symbols and tirp_obj.get_rels() == rels:
                    return [tirp_obj]
