import csv, os
from itertools import islice

from werkzeug.utils import secure_filename

from flask import current_app

from karmalegoweb.src.type_validation import (
    check_float,
    check_non_negative_int,
)


class knowledge_based_file:
    def __init__(self, knowledgebase, dir_path) -> None:
        knowledgebase.filename = secure_filename("states_knowledge_based.csv")
        
        self.path = os.path.join(dir_path, knowledgebase.filename)
        self.disc_path = dir_path
        knowledgebase.save(self.path)

    def validate_header(self):
        """
        Validates that the header of a user-submitted knowledge-based discretization file's header
        adheres to HugoBot's standards.
        :param kb_file_path: a path to the knowledge-based file
        :return: True if the header fits the format, False otherwise
        """
        with open(self.path) as kb_file:
            reader = csv.reader(kb_file, delimiter=",")
            for header in islice(reader, 0, 1):

                # solves a utf-8-bom encoding issue where ï»¿ gets added in the beginning of .csv files.
                state_id_to_compare = header[0].replace("ï»¿", "")

                # StateID, TemporalPropertyID, Method, BinID, BinLow, BinHigh
                if (
                    len(header) == 6
                    and current_app.config["KB_HEADER_FORMAT"][0] in state_id_to_compare
                    and header[1] == current_app.config["KB_HEADER_FORMAT"][1]
                    and header[2] == current_app.config["KB_HEADER_FORMAT"][3]
                    and header[3] == current_app.config["KB_HEADER_FORMAT"][4]
                    and header[4] == current_app.config["KB_HEADER_FORMAT"][5]
                    and header[5] == current_app.config["KB_HEADER_FORMAT"][6]
                ):
                    return True

                # StateID, TemporalPropertyID, Method, BinID, BinLow, BinHigh, BinLowScore
                if (
                    len(header) == 7
                    and current_app.config["KB_HEADER_FORMAT"][0] in state_id_to_compare
                    and header[1] == current_app.config["KB_HEADER_FORMAT"][1]
                    and header[2] == current_app.config["KB_HEADER_FORMAT"][3]
                    and header[3] == current_app.config["KB_HEADER_FORMAT"][4]
                    and header[4] == current_app.config["KB_HEADER_FORMAT"][5]
                    and header[5] == current_app.config["KB_HEADER_FORMAT"][6]
                    and header[6] == current_app.config["KB_HEADER_FORMAT"][7]
                ):
                    return True

                # StateID, TemporalPropertyID, Method, BinID, BinLow, BinHigh, BinLowScore, BinLabel
                if (
                    len(header) == 8
                    and current_app.config["KB_HEADER_FORMAT"][0] in state_id_to_compare
                    and header[1] == current_app.config["KB_HEADER_FORMAT"][1]
                    and header[2] == current_app.config["KB_HEADER_FORMAT"][3]
                    and header[3] == current_app.config["KB_HEADER_FORMAT"][4]
                    and header[4] == current_app.config["KB_HEADER_FORMAT"][5]
                    and header[5] == current_app.config["KB_HEADER_FORMAT"][6]
                    and header[6] == current_app.config["KB_HEADER_FORMAT"][7]
                    and header[7] == current_app.config["KB_HEADER_FORMAT"][8]
                ):
                    return True

                # StateID, TemporalPropertyID, TemporalPropertyName Method, BinID, BinLow, BinHigh, BinLowScore, BinLabel
                if (
                    len(header) == 9
                    and current_app.config["KB_HEADER_FORMAT"][0] in state_id_to_compare
                    and header[1] == current_app.config["KB_HEADER_FORMAT"][1]
                    and header[2] == current_app.config["KB_HEADER_FORMAT"][2]
                    and header[3] == current_app.config["KB_HEADER_FORMAT"][3]
                    and header[4] == current_app.config["KB_HEADER_FORMAT"][4]
                    and header[5] == current_app.config["KB_HEADER_FORMAT"][5]
                    and header[6] == current_app.config["KB_HEADER_FORMAT"][6]
                    and header[7] == current_app.config["KB_HEADER_FORMAT"][7]
                    and header[8] == current_app.config["KB_HEADER_FORMAT"][8]
                ):
                    return True

                return False

    def validate_body(self, vmap_path):
        """
        Validates that the header of a user-submitted gradient discretization file's body
        adheres to HugoBot's standards.
        :param kb_file_path: a path to the knowledge-based file
        :param disc_path: a path to the discretization folder
        :param vmap_path: a path to the dataset's variable map file (needed for some validation paths)
        :return: True if every row:
        # Has a non-negative integer as its 1st element
        # Has a non-negative integer as its 2nd element
        # OPTIONAL has a Temporal Property Name as its 3rd element
            that fits the Name defined in the VMap for the ID in the same row
        # Has 'knowledge-based' as the 3rd element
        # Has a non-negative integer as its 4th element
        # Has a floating point number as its 5th element
        # Has a floating point number as its 6th element
        # OPTIONAL has a string describing the state as its 8th element
        False otherwise
        """
        is_labeled = False
        has_vmap_names = False
        with open(self.path) as kb_file:
            reader = csv.reader(kb_file, delimiter=",")

            i = 0
            flag = True
            vmap = {}
            for row in reader:
                if i == 0:
                    if row[2] == "TemporalPropertyName":
                        has_vmap_names = True
                    if (len(row) == 8 and row[7] == "BinLabel") or (
                        len(row) == 9 and row[8] == "BinLabel"
                    ):
                        is_labeled = True
                        vmap = self.__get_variable_map(vmap_path)
                    i = i + 1
                    continue

                j = 0

                flag &= check_non_negative_int(row[j])
                j = j + 1
                flag &= check_non_negative_int(row[j])
                j = j + 1

                if is_labeled and has_vmap_names:
                    # If the file has labels and VMap variables we have to validate the VMap variables
                    flag &= vmap[row[j - 1]] == row[j]
                    j = j + 1

                flag &= row[j] == "knowledge-based"
                j = j + 1
                flag &= check_non_negative_int(row[j])
                j = j + 1
                flag &= check_float(row[j]) or row[j] == "#NAME?"  # workaround for -inf in excel
                j = j + 1
                flag &= check_float(row[j])
                j = j + 1

                i = i + 1
        if is_labeled and not has_vmap_names:
        # add the variable names ourselves in case there are labels but no variable names
            add_variable_names_to_vmap(self.path, self.disc_path, vmap)
        return flag

    def __get_variable_map(self, vmap_path):
        """
        Receives a path to a variable map file and returns a dictionary that maps each id to its name (both are unique)
        :param vmap_path: a path to the variable map file
        :return: a <string,string> dictionary that maps IDs to names
        """
        with open(vmap_path) as vmap:
            variable_dic = {}
            reader = csv.reader(vmap, delimiter=",")
            i = 0
            for row in reader:
                if i == 0:
                    # ignore header
                    i = i + 1
                    continue
                variable_dic[row[0]] = row[1]
            vmap.close()
            return variable_dic


def add_variable_names_to_vmap(kb_file_path, disc_path, vmap):
    """
    Receives a knowledge-based file with bin labels and a dictionary of a the variables and modifies the file,
    such that it contains a column with the corresponding variable names.
    :param kb_file_path: a path to the knowledge-based file
    :param disc_path: a path to the discretization folder
    :param vmap: a <string,string> dictionary that maps a variable ID to its variable name, as defined in the VMap file.
    :return:
    """
    with open(kb_file_path) as original_file:
        reader = csv.reader(original_file, delimiter=",")
        with open(os.path.join(disc_path, "states_kb_temp.csv"), "w", newline="") as new_file:
            writer = csv.writer(new_file, delimiter=",")

            i = 0
            for row in reader:
                if i == 0:
                    row.insert(2, "TemporalPropertyName")
                    writer.writerow(row)
                    i = i + 1
                    continue
                variable_name = vmap[row[1]]
                row.insert(2, variable_name)
                writer.writerow(row)
                # modify the row to contain the new column

    # Replace the old file
    os.remove(kb_file_path)
    os.rename(os.path.join(disc_path, "states_kb_temp.csv"), kb_file_path)
