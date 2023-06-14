import os
from karmalegoweb.src.discretization.discretization_builder import discretization_builder


class knowledge_based(discretization_builder):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "Knowledge-Based"

    def make(self, interpolation_gap, paa, knowledge_based_file):
        os.mkdir(self.disc_path)
        steps = [
            lambda: self.set_interpolation_gap(interpolation_gap),
            lambda: self.set_paa(paa),
            lambda: self.set_knowledge_based_file(knowledge_based_file),
            lambda: self.save_discretization_in_db(),
        ]
        for step in steps:
            scc, err = step()
            if not scc:
                return scc, err

        return True, ":)"
