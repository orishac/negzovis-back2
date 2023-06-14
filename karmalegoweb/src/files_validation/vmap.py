import csv
from itertools import islice

from flask import current_app

from karmalegoweb.src.utils import get_variable_list


def validate_header(vmap_path):
    """
    Validates that the header of a user-submitted variable map file adheres to HugoBot's standards.
    :param vmap_path: a path to the variable map file
    :return: True if the header fits one of the formats, False otherwise
    """

    with open(vmap_path) as vmap:
        reader = csv.reader(vmap, delimiter=",")
        # TODO: Change this so that he will find the first row instead of this implementation...
        for header in islice(reader, 0, 1):

            # solves a utf-8-bom encoding issue where ï»¿ gets added in the beginning of .csv files.
            variable_id_to_compare = header[0].replace("ï»¿", "")

            if len(header) == len(current_app.config["VMAP_HEADER_FORMAT"]):
                if current_app.config["VMAP_HEADER_FORMAT"][0] in variable_id_to_compare:
                    if header[1] == current_app.config["VMAP_HEADER_FORMAT"][1]:
                        if header[2] == current_app.config["VMAP_HEADER_FORMAT"][2]:
                            return True

            if len(header) == len(current_app.config["VMAP_HEADER_FORMAT_2"]):
                if current_app.config["VMAP_HEADER_FORMAT_2"][0] in variable_id_to_compare:
                    if header[1] == current_app.config["VMAP_HEADER_FORMAT_2"][1]:
                        if header[2] == current_app.config["VMAP_HEADER_FORMAT_2"][2]:
                            return True
            return False


def validate_id_integrity(raw_data_path, vmap_path):
    """
    Validates whether or not a user has attended to each and every variable in the raw data file
    in his submitted variable map file.
    :param raw_data_path: a path to the raw data file
    :param vmap_path: a path to the variable map file
    :return: True if the list of variables match, False otherwise
    """
    raw_data_variable_list = get_variable_list(raw_data_path, 1)
    vmap_variable_list = get_variable_list(vmap_path, 0)
    return sorted(raw_data_variable_list) == sorted(vmap_variable_list)
