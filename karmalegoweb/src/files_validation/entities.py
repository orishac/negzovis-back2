import csv
from itertools import islice

from karmalegoweb.src.utils import get_variable_list


def validate_id_column(entities_path) -> bool:
    with open(entities_path) as entities:
        reader = csv.reader(entities, delimiter=",")
        for header in islice(reader, 0, 1):

            # solves a utf-8-bom encoding issue where ï»¿ gets added in the beginning of .csv files.
            entity_id_to_compare = header[0].replace("ï»¿", "")

            if entity_id_to_compare != "id":
                # if "id" not in entity_id_to_compare:
                entities.close()
                return False
    return True


def validate_id_integrity(raw_data_path, entities_path) -> bool:
    """
    Validates whether or not a user has attended to each and every entity in the raw data file
    in his submitted entity file.

    :return: True if the list of entities match, False otherwise
    """

    raw_data_entity_list = get_variable_list(raw_data_path, 0)
    entity_list = get_variable_list(entities_path, 0)

    return sorted(raw_data_entity_list) == sorted(entity_list)
