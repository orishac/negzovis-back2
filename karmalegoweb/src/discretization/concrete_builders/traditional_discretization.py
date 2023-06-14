import os
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
