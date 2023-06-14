import os

from flask import current_app
from karmalegoweb.src.discretization.discretization_builder import discretization_builder


class traditional_discretization(discretization_builder):
    def make(self, interpolation_gap, paa, num_states):
        os.mkdir(self.disc_path)
        steps = [
            lambda: self.set_interpolation_gap(interpolation_gap),
            lambda: self.set_paa(paa),
            lambda: self.set_num_states(num_states),
            lambda: self.save_discretization_in_db(),
        ]
        for step in steps:
            scc, err = step()
            if not scc:
                return scc, err

        return True, ":)"
    

class empty_discretization(discretization_builder):
    def make(self):
        os.mkdir(self.disc_path)
        steps = [
            lambda: self.save_discretization_in_db(),
        ]
        for step in steps:
            scc, err = step()
            if not scc:
                return scc, err

        return True, ":)"


class persist(traditional_discretization):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "Persist"


class kmeans(traditional_discretization):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "KMeans"


class equal_width(traditional_discretization):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "Equal Width"


class equal_frequency(traditional_discretization):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "Equal Frequency"


class sax(traditional_discretization):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "SAX"

class empty(empty_discretization):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "Sequential"

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
        command += " " + str(1)
        command += " " + str(1)

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
            " " + 'equal-width'
        )
        command += " " + str(2)

        return command


# -------------------------------------- TD4C --------------------------------------
class td4c(traditional_discretization):
    def make(self, interpolation_gap, paa, num_states):
        scs, err = self.validate_classes_in_raw_data()
        if not scs:
            return scs, err
        return super().make(interpolation_gap, paa, num_states)


class td4c_cosine(td4c):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "TD4C-Cosine"


class td4c_diffmax(td4c):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "TD4C-Diffmax"


class td4c_diffsum(td4c):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "TD4C-Diffsum"


class td4c_entropy(td4c):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "TD4C-Entropy"


class td4c_entropy_ig(td4c):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "TD4C-Entropy-IG"


class td4c_skl(td4c):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "TD4C-SKL"
