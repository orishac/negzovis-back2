from collections import defaultdict
import csv
from itertools import islice
import os

from flask import current_app

from karmalegoweb.src.utils import get_variable_list
from karmalegoweb.src.type_validation import check_float, check_int, check_non_negative_int


def validate_data_header(raw_data_path) -> bool:
    """
    Validates that the header of a user-submitted raw data file adheres to HugoBot's standards.
    :param raw_data_path: a path to the raw data file
    :return: True if the header fits the format, False otherwise
    """

    with open(raw_data_path) as data:
        reader = csv.reader(data, delimiter=",")
        for header in islice(reader, 0, 1):

            # solves a utf-8-bom encoding issue where ï»¿ gets added in the beginning of .csv files.
            entity_id_to_compare = header[0].replace("ï»¿", "")

            HEADER_FORMAT = current_app.config["RAW_DATA_HEADER_FORMAT"]

            if len(header) == len(HEADER_FORMAT):
                if HEADER_FORMAT[0] in entity_id_to_compare:
                    if (header[1], header[2], header[3]) == (
                        HEADER_FORMAT[1],
                        HEADER_FORMAT[2],
                        HEADER_FORMAT[3],
                    ):
                        return True
            return False


def validate_data_body(raw_data_path) -> bool:
    """
    Validates the integrity of the data in the raw data file it
    :param raw_data_path: a path to the raw data file
    :return: True if every row:
    # Has a non-negative integer as its 1st element
    # Has an integer as its 2nd element
    # Has a non-negative integer as its 3rd element
    # Has a floating point number as its 4th element
    False otherwise
    """

    with open(raw_data_path) as data:
        reader = csv.reader(data, delimiter=",")
        i = 0
        flag = True
        for row in reader:
            if i == 0:
                i = i + 1
                continue
            flag &= check_non_negative_int(row[0])
            flag &= check_int(row[1])
            flag &= check_non_negative_int(row[2])
            flag &= check_float(row[3])
            i = i + 1
        return flag


def get_properties_list(raw_data_path):
    column_in_data = 1
    list_to_return = get_variable_list(raw_data_path, column_in_data)
    list_to_return = [int(x) for x in list_to_return]
    list_to_return = sorted(list_to_return)
    return list_to_return


def convert_to_negative(raw_data_path, dir_path):
    unsorted_dict = defaultdict(list)

    with open(raw_data_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            entID, event, timestamp = row[0], row[1], row[2]
            unsorted_dict[(entID, timestamp)].append(event)

    sorted_dict = dict(sorted(unsorted_dict.items(), key=lambda x: (int(x[0][0]), int(x[0][1]))))

    negative_path = os.path.join(dir_path, 'negative.ascii')

    with open(negative_path, 'w') as f:
        for key, value in sorted_dict.items():
            entID, timestamp = key[0], key[1]
            f.write(f"{entID} {timestamp} {len(value)} {' '.join(value)} \n")

    return True



