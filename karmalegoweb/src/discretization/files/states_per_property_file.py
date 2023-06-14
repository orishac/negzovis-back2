import csv, os
from itertools import islice

from werkzeug.utils import secure_filename

from flask import current_app

from karmalegoweb.src.type_validation import (
    check_float,
    check_non_negative_int,
)


class states_per_property_file:
    def __init__(self, states_per_property_raw, dir_path) -> None:
        states_per_property_raw.filename = secure_filename("states_per_property.csv")
        self.path = os.path.join(dir_path, states_per_property_raw.filename)
        states_per_property_raw.save(self.path)

    def validate_header(self):
        """
        Validates that the header of a user-submitted gradient discretization file's header adheres to HugoBot's standards.
        :param gradient_file_path: a path to the gradient file
        :return: True if the header fits one of the formats, False otherwise
        """
        with open(self.path) as gradient_file:
            reader = csv.reader(gradient_file, delimiter=",")
            for header in islice(reader, 0, 1):

                # solves a utf-8-bom encoding issue where ï»¿ gets added in the beginning of .csv files.
                state_id_to_compare = header[0].replace("ï»¿", "")

                if (
                    len(header) <= 7
                    and current_app.config["GRADIENT_HEADER_FORMAT"][0] in state_id_to_compare
                ):
                    if header[1] == current_app.config["GRADIENT_HEADER_FORMAT"][1]:
                        if header[2] == current_app.config["GRADIENT_HEADER_FORMAT"][2]:
                            if header[3] == current_app.config["GRADIENT_HEADER_FORMAT"][3]:
                                if header[4] == current_app.config["GRADIENT_HEADER_FORMAT"][4]:
                                    if header[5] == current_app.config["GRADIENT_HEADER_FORMAT"][5]:
                                        if (
                                            len(header) == 6
                                            or header[6]
                                            == current_app.config["GRADIENT_HEADER_FORMAT"][6]
                                        ):
                                            return True
                return False

    def validate_body(self):
        """
        Validates that the header of a user-submitted gradient discretization file's body
        adheres to HugoBot's standards.
        :param gradient_file_path: a path to the gradient file
        :return: True if every row:
        # Has a non-negative integer as its 1st element
        # Has a non-negative integer as its 2nd element
        # Has 'gradient' as the 3rd element
        # Has a non-negative integer as its 4th element
        # Has a floating point number between -90 and 90 as its 5th element
        # Has a floating point number between -90 and 90 as its 6th element
        False otherwise
        """
        with open(self.path) as gradient_file:
            reader = csv.reader(gradient_file, delimiter=",")

            i = 0
            flag = True
            for row in reader:
                if i == 0:
                    i = i + 1
                    continue

                flag &= check_non_negative_int(row[0])
                flag &= check_non_negative_int(row[1])
                flag &= (row[2] == "gradient") or (row[2] == "knowledge-based")
                flag &= check_non_negative_int(row[3])
                flag &= check_float(row[4]) and (float(row[4]) >= -90) and (float(row[4]) <= 90)
                flag &= check_float(row[5]) and (float(row[5]) >= -90) and (float(row[5]) <= 90)

                i = i + 1

        return flag
