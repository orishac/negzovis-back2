import json


def parse_states_file(path):
    """
    This function parses the state file and init the states dictionary. The file must contain the columns - StateID, TemporalPropertyName, BinLabel
    :return:
    """
    states = {}
    states_by_name = {}
    with open(path + "/states.json", "r") as states_file:
        states_json = json.load(states_file)
        for state in states_json:
            state_id = state["StateID"]
            if "TemporalPropertyName":
                first_part = state["TemporalPropertyName"].rstrip()
            else:
                first_part = state["TemporalPropertyID"]
            if "BinLabel" in state:
                second_part = state["BinLabel"].rstrip()
            else:
                second_part = state["BinID"].rstrip()
            state_name = f"{first_part}.{second_part}"
            states_by_name[state_name] = state_id
            states[state_id] = state_name

    return states, states_by_name
