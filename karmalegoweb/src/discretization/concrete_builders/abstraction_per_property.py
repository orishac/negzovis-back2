import os

from karmalegoweb.src.discretization.discretization_builder import discretization_builder


class abstraction_per_property(discretization_builder):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "Abstraction Per Property"

    def make(self, preprocessing_file, states_per_propert_file, abstraction_file):
        os.mkdir(self.disc_path)
        steps = [
            lambda: self.set_preprocessing_file(preprocessing_file),
            lambda: self.set_abstraction_file(abstraction_file),
            lambda: self.set_states_per_property_file(states_per_propert_file)
            if states_per_propert_file is not None
            else None,
            lambda: self.save_discretization_in_db(),
        ]

        for step in steps:
            scc, err = step()
            if not scc:
                return scc, err

        return True, ":)"
