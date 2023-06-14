import os
from karmalegoweb.src.discretization.discretization_builder import discretization_builder


class gradient(discretization_builder):
    def __init__(self, dataset_name) -> None:
        super().__init__(dataset_name)
        self.abstraction_method = "Gradient"

    def make(self, interpolation_gap, paa, gradient_window_size, gradient_file, num_states):
        os.mkdir(self.disc_path)
        steps = [
            lambda: self.set_interpolation_gap(interpolation_gap),
            lambda: self.set_paa(paa),
            lambda: self.set_gradient_window_size(gradient_window_size),
            lambda: self.set_gradient_file(gradient_file),
            lambda: self.set_num_states(num_states),
            lambda: self.save_discretization_in_db()
        ]
        for step in steps:
            scc, err = step()
            if not scc:
                return scc, err

        return True, ":)"
