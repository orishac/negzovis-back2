from karmalegoweb.src.manage_data.save_data import create_settings
from flask import g

DEFAULT_CLASS_0_NAME = "Cohort"
DEFAULT_CLASS_1_NAME = "Control"
DEFAULT_TIME_STAMP = "Minutes"


class settings:
    def __init__(self, dataset_name, tim_class0, tim_class1, two_class, has_entities) -> None:
        # Therese shouldn't be a difference between the paramters of class 0 and class 1 in the current version
        self.dataset_name = dataset_name
        self.username = f"{g.user.FName} {g.user.LName}"
        self.two_class = two_class
        self.has_entities = has_entities
        self.class_0_name = DEFAULT_CLASS_0_NAME
        self.class_1_name = DEFAULT_CLASS_1_NAME
        self.timestamp = DEFAULT_TIME_STAMP
        self.min_ver_support = 1
        self.num_of_relations = 1
        self.max_gap = 1
        self.num_of_entities_class_0 = 1
        self.num_of_entities_class_1 =  1

    def save(self, visualization_id):
        create_settings(self.dataset_name, visualization_id, self.__dict__)
