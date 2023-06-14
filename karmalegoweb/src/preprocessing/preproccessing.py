import os

from flask import current_app

from karmalegoweb.src.preprocessing.results import preprocessins_results
from karmalegoweb.src.preprocessing.composer import compose
from karmalegoweb.src.preprocessing.parser import parse
from karmalegoweb.src.preprocessing.KLOutputToSearchIndexFile import KLOutputToSearchIndexFile
from karmalegoweb.src.manage_data.save_data import (
    create_empty_visualization,
    create_entities,
    create_states,
    finish_preproccess_run,
)
from karmalegoweb.src.manage_data.translate_data import (
    karmalego_to_discretization,
    karmalego_to_dataset_name,
)
from karmalegoweb.src.manage_data.data_checks import (
    is_two_class,
    has_entities,
)
from karmalegoweb.src.preprocessing.settings import settings
from karmalegoweb.src.preprocessing.prerequisites import validate as validate_prerequisites
from karmalegoweb.src.preprocessing.tirps import create_tree_structures, merge_trees, save_tree

from karmalegoweb.src.views.tali import call_tali_preprocess


class preprocessing:
    """
    This class is the starting point of the preprocessing before you can visualize your data.
    The process takes as input the output from Karmalego and creates as output organized data for the visualization to use.
    In particular it organizes data about the settings, entities, states, index files for searching purposes
    and most importantly a tree structured data of the tirp.

    The proccess includes:
    - Parsing karmalego's output
    - Creating and saving settings
    - Organizing and saving entities and states
    - Organizing the tirps into a tree structure
    - Calculating extra parameters that are used in the visualization like offsets of the intervals from each other
    - Creating index files that helps searching tirps efficiently
    - Saving the tree structure

    Recreated by Ravid 03/2022
    """

    def __init__(self, karmalego_id) -> None:
        self.karmalego_id = karmalego_id
        self.dataset_name = karmalego_to_dataset_name(karmalego_id)
        self.discretization_id = karmalego_to_discretization(karmalego_id)
        self.two_class = is_two_class(self.dataset_name)
        self.has_entities = has_entities(self.dataset_name)
        self.visualization = None
        self.tim_class0_parsed = None
        self.tim_class1_parsed = None

        self.tree = None

    def start(self):
        try:
            result = validate_prerequisites(self.karmalego_id)
            current_app.logger.debug("PREPROCESSING - Validated")
            if result != preprocessins_results.GOOD:
                return result, None
            self.__create_run()

            self.__parse()

            self.__create_settings_file()
            entities = None
            if self.has_entities:
                entities = create_entities(self.dataset_name, self.visualization.id)
                current_app.logger.debug("PREPROCESSING - Created Entities File")
            create_states(self.dataset_name, self.discretization_id, self.visualization.id)
            current_app.logger.debug("PREPROCESSING - Created States File")
            self.__create_tree_structures()
            self.__calculate_extra_parameters(entities)
            self.__create_search_files()

            save_tree(self.dataset_name, self.visualization.id, self.tree)
            current_app.logger.debug("PREPROCESSING - Saved Tirps Tree")

            # calling Tali's preprocess to start
            call_tali_preprocess(
                visualization_id=self.visualization.id, dataset_name=self.dataset_name
            )

            finish_preproccess_run(self.visualization.id, True)

            return preprocessins_results.GOOD, self.visualization.id

        except Exception as e:
            if self.visualization is not None:
                finish_preproccess_run(self.visualization.id, False, str(e))
            current_app.log_exception(e)
            return preprocessins_results.EXCEPTION, None

    def __create_run(self):
        self.visualization = create_empty_visualization(self.karmalego_id, self.dataset_name)
        current_app.logger.debug("PREPROCESSING - Run Created")

    def __parse(self):
        if self.two_class:
            self.tim_class0_parsed = parse(self.karmalego_id, 0)
            current_app.logger.debug("PREPROCESSING - Input Class 1 Parsed")
            self.tim_class1_parsed = parse(self.karmalego_id, 1)
            current_app.logger.debug("PREPROCESSING - Input Class 2 Parsed")
        else:
            self.tim_class0_parsed = parse(self.karmalego_id)
            current_app.logger.debug("PREPROCESSING - Input Parsed")

    def __create_settings_file(self):
        settings_object = settings(
            self.dataset_name,
            self.tim_class0_parsed,
            self.tim_class1_parsed,
            self.two_class,
            self.has_entities,
        )
        settings_object.save(self.visualization.id)
        current_app.logger.debug("PREPROCESSING - Created settings file")

    def __create_tree_structures(self):
        tirps_cls0 = [tirp.to_tim_cls0() for tirp in self.tim_class0_parsed.tirps]
        tirps_root_cls0 = create_tree_structures(tirps_cls0)

        current_app.logger.debug("PREPROCESSING - Organized Class 0 To a Tree Data Structure ")

        if self.two_class:
            tirps_cls1 = [tirp.to_tim_cls1() for tirp in self.tim_class1_parsed.tirps]
            tirps_root_cls1 = create_tree_structures(tirps_cls1)
            current_app.logger.debug("PREPROCESSING - Organized Class 1 To a Tree Data Structure ")
            tree = merge_trees(tirps_root_cls0, tirps_root_cls1)
            current_app.logger.debug("PREPROCESSING - Merged Trees ")
        else:
            tree = tirps_root_cls0

        self.tree = tree

    def __calculate_extra_parameters(self, entities):
        for tirp in self.tree:
            tirp.calculate_extensions(entities)
        current_app.logger.debug("PREPROCESSING - Calculated Extra Parameters")

    def __create_search_files(self):
        # KLOutputToSearchIndexFile is outdated and needs as input an old output version of karmalego.
        # Therefore, before creating the search index files the old output is created using the compose function.
        # KLOutputToSearchIndexFile was written by Dor

        visualization_path = os.path.join(
            current_app.config["DATASETS_ROOT"],
            self.dataset_name,
            "visualizations",
            self.visualization.id,
        )

        # Creating the old karmalego output for the search algorithm
        old_kl_output_cls0 = compose(self.tim_class0_parsed)
        current_app.logger.debug("PREPROCESSING - Composed Karmalego's Old Output For Class 0 ")
        path_kl_cls0 = os.path.join(visualization_path, "KLoutput_class0")
        with open(path_kl_cls0, "w") as f:
            f.write(old_kl_output_cls0)
        output_search_cls0 = os.path.join(visualization_path, "search_index_class0")

        KLOutputToSearchIndexFile(
            input_file_path=path_kl_cls0,
            output_file_path=output_search_cls0,
            num_of_entities=self.tim_class0_parsed.num_of_entities,
            tree=self.tree,
        )

        current_app.logger.debug("PREPROCESSING - Created Search Files For Class 0 ")

        if self.two_class:
            old_kl_output_cls1 = compose(self.tim_class1_parsed)
            current_app.logger.debug("PREPROCESSING - Composed Karmalego's Old Output For Class 1 ")
            path_kl_cls1 = os.path.join(visualization_path, "KLoutput_class1")
            with open(path_kl_cls1, "w") as f:
                f.write(old_kl_output_cls1)
            output_search_cls1 = os.path.join(visualization_path, "search_index_class1")

            KLOutputToSearchIndexFile(
                input_file_path=path_kl_cls1,
                output_file_path=output_search_cls1,
                num_of_entities=self.tim_class1_parsed.num_of_entities,
                tree=self.tree,
            )

            current_app.logger.debug("PREPROCESSING - Created Search Files For Class 1 ")
