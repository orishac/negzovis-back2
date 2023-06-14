import csv, inspect, os
from uuid import uuid4
from werkzeug.utils import secure_filename

from flask import current_app

from karmalegoweb.src.db import get_db
from karmalegoweb.src.discretization.files.knowledge_based_file import (
    knowledge_based_file,
)
from karmalegoweb.src import models
from karmalegoweb.src.discretization.files.gradient_file import gradient_file
from karmalegoweb.src.discretization.files.states_per_property_file import (
    states_per_property_file,
)
from karmalegoweb.src.type_validation import check_non_negative_int


def some_value(func):
    def inner(self, value):
        value_name = list(inspect.signature(func).parameters.keys())[1]
        if value is None:
            return False, f"Missing {value_name}"
        error = func(self, value)
        if error is None:
            return True, ":)"
        return error

    return inner


class discretization_builder:
    def __init__(self, dataset_name) -> None:
        self.id = str(uuid4())
        self.dataset_name = dataset_name
        self.dataset_path = os.path.join(current_app.config["DATASETS_ROOT"], dataset_name)
        self.disc_path = os.path.join(self.dataset_path, self.id)

        self.abstraction_method = "unset"

        self.abstraction_filename = None
        self.preprocessing_filename = None
        self.states_filename = None
        self.gradient_filename = None
        self.knowledged_based_filename = None

        self.abstraction_file_path = None
        self.preprocessing_file_path = None
        self.states_file_path = None
        self.gradient_file_path = None
        self.knowledged_based_file_path = None

        self.paa = None
        self.interpolation_gap = None
        self.num_states = None

        self.gradient_window_size = None

    # -------------------- Set Properties --------------------

    @some_value
    def set_paa(self, paa):
        if not check_non_negative_int(paa) or paa < 1:
            return False, "PAA has to be a positive integer larger than 1"
        self.paa = paa

    @some_value
    def set_interpolation_gap(self, interpolation_gap):
        if not check_non_negative_int(interpolation_gap) or interpolation_gap < 1:
            return False, "Interpolation Gap has to be a positive integer of at least 1"
        self.interpolation_gap = interpolation_gap

    @some_value
    def set_num_states(self, num_states):
        if not check_non_negative_int(num_states) or num_states < 2:
            return False, "Number of States has to be a positive integer of at least 2"
        self.num_states = num_states

    @some_value
    def set_gradient_window_size(self, gradient_window_size):
        if not check_non_negative_int(gradient_window_size) or gradient_window_size < 2:
            return False, "Gradient window size has to be a positive integer of at least 2"
        self.gradient_window_size = gradient_window_size

    @some_value
    def set_gradient_file(self, gradient_file_raw):
        gradient_file_obj = gradient_file(gradient_file_raw, self.disc_path)
        if not gradient_file_obj.validate_header():
            return False, "the gradient file you supplied has an incorrect header."

        if not gradient_file_obj.validate_body():
            return False, "the gradient file you supplied has incorrect data."

        self.gradient_filename = gradient_file_raw.filename
        self.gradient_file_path = gradient_file_obj.path

    @some_value
    def set_preprocessing_file(self, preprocessing_file):
        preprocessing_file.filename = secure_filename("preprocessing_per_property.csv")
        preprocessing_per_property_path = os.path.join(self.disc_path, preprocessing_file.filename)
        preprocessing_file.save(preprocessing_per_property_path)
        self.preprocessing_filename = preprocessing_file.filename
        self.preprocessing_file_path = preprocessing_per_property_path

    @some_value
    def set_abstraction_file(self, abstraction_file):
        abstraction_file.filename = secure_filename("abstraction_per_property.csv")
        abstraction_per_property_path = os.path.join(self.disc_path, abstraction_file.filename)
        abstraction_file.save(abstraction_per_property_path)
        self.abstraction_filename = abstraction_file.filename
        self.abstraction_file_path = abstraction_per_property_path

    @some_value
    def set_states_per_property_file(self, states_file_raw):
        states_file_obj = states_per_property_file(states_file_raw, self.disc_path)

        if not states_file_obj.validate_header():
            return False, "the states file you supplied has an incorrect header."

        if not states_file_obj.validate_body():
            return False, "the states file you supplied has incorrect data."

        self.states_filename = states_file_raw.filename
        self.states_file_path = states_file_obj.path

    @some_value
    def set_knowledge_based_file(self, knowledge_based_raw):
        knowledged_based = knowledge_based_file(knowledge_based_raw, self.disc_path)
        if not knowledged_based.validate_header():
            return False, "the knowledge-based file you supplied has an incorrect data."
        vmap_path = os.path.join(self.dataset_path, "VMap.csv")
        if not knowledged_based.validate_body(vmap_path):
            return False, "the knowledge-based file you supplied has incorrect fields."

        self.knowledged_based_filename = knowledge_based_raw.filename
        self.knowledged_based_file_path = knowledged_based.path

    # -------------------- Save Discretization --------------------

    def save_discretization_in_db(self):
        dataset = models.info_about_datasets.query.filter_by(Name=self.dataset_name).first()
        discretization = models.discretization.query.filter_by(
            AbMethod=self.abstraction_method,
            dataset=dataset,
            GradientFile_name=self.gradient_filename,
            InterpolationGap=self.interpolation_gap,
            KnowledgeBasedFile_name=self.knowledged_based_filename,
            NumStates=self.num_states if self.num_states is not None else 0,
            PAA=self.paa,
            GradientWindowSize=self.gradient_window_size
            if self.gradient_window_size is not None
            else 0,
        ).first()

        if self.abstraction_method != "Gradient" and \
            self.abstraction_method != "Knowledge-Based" and \
            self.abstraction_method != "Abstraction Per Property" and \
            discretization is not None:
            return (
                False,
                "Discretization file for this dataset with the same parameters already exist",
            )

        disc = models.discretization(
            id=self.id,
            dataset=dataset,
            AbMethod=self.abstraction_method,
            InterpolationGap=self.interpolation_gap,
            NumStates=self.num_states if self.num_states is not None else 0,
            PAA=self.paa,
            GradientWindowSize=self.gradient_window_size
            if self.gradient_window_size is not None
            else 0,
            GradientFile_name=self.gradient_filename,
            KnowledgeBasedFile_name=self.knowledged_based_filename,
        )
        run = models.discretization_status(discretization_id=self.id)
        db = get_db()
        db.session.add(disc)
        db.session.add(run)
        return True, "Discretization Saved"

    # -------------------- Get Result --------------------
    def get_hugobot_command(self):
        command = "python"
        command += " " + current_app.config["CLI_PATH"]
        command += " " + current_app.config["MODE"]
        command += " " + os.path.join(self.dataset_path, self.dataset_name + ".csv")
        command += " " + self.disc_path

        if self.preprocessing_filename is not None:
            command += " per-property"
            if self.states_file_path is not None:
                command += " -s"
                command += " " + self.states_file_path

            if self.preprocessing_file_path is not None:
                command += " " + self.preprocessing_file_path

            if self.abstraction_file_path is not None:
                command += " " + self.abstraction_file_path
            return command

        command += " " + current_app.config["DATASET_OR_PROPERTY"]
        command += " " + current_app.config["PAA_FLAG"]
        command += " " + str(self.paa)
        command += " " + str(self.interpolation_gap)

        if self.gradient_filename is not None:
            command += " " + current_app.config["GRADIENT_PREFIX"]
            command += " " + current_app.config["GRADIENT_FLAG"]
            command += " " + self.gradient_file_path
            command += " " + str(self.gradient_window_size)
            return command

        if self.knowledged_based_filename is not None:
            command += " " + current_app.config["KB_PREFIX"]
            command += " " + self.knowledged_based_file_path
            return command

        command += " " + current_app.config["DISCRETIZATION_PREFIX"]
        command += (
            " " + current_app.config["ABSTRACTION_METHOD_CONVERSION"][self.abstraction_method]
        )
        command += " " + str(self.num_states)

        return command

    # -------------------- Additional Validations --------------------
    def __get_variable_list(self, path, column):
        """
        Receives a path to a raw data file and a column and extracts a list of unique values in that column
        :param data_path: a path to the raw data file
        :param column: the column which we want to get unique values from
        :return: a list of all unique value
        """
        with open(path) as data:
            variable_list = []
            reader = csv.reader(data, delimiter=",")
            for row in reader:
                variable_list.append(row[column])
            variable_list = variable_list[1:]  # truncate header
            variable_list = list(set(variable_list))  # remove duplicates
            data.close()
            return variable_list

    def validate_classes_in_raw_data(self):
        """
        Validates whether or not a given raw data file is divided into classes
        :param raw_data_path: a path to the raw data file
        :return: True if for every entity, there exists a row such that:
        # The entity ID is the first element
        # The Variable ID is -1
        # The Timestamp is 0
        # The class is a non-negative integer
        False otherwise
        """
        raw_data_path = os.path.join(self.dataset_path, self.dataset_name + ".csv")
        entity_list = self.__get_variable_list(raw_data_path, 0)
        with open(raw_data_path) as data:
            reader = csv.reader(data, delimiter=",")
            i = 0
            for row in reader:
                if i == 0:
                    i = i + 1
                    continue
                entity = row[0]
                if row[1] == "-1":
                    if row[2] == "0":
                        if check_non_negative_int(row[3]):
                            entity_list.remove(entity)
        validates_successfully = len(entity_list) == 0
        if not validates_successfully:
            return (
                False,
                "TD4C requires classification labeling in the data (TemporalPropertyID=-1).",
            )
        return True, ":)"
