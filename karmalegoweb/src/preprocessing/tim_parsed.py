from dataclasses import dataclass, field
from karmalegoweb.src.preprocessing.tirp import tirp as tirp_object, tirp_stats


@dataclass
class tim:
    input_path: str
    min_ver_support: float
    num_relations: int
    max_gap: int
    label: str
    epsilon: int
    output_path: str
    incremental_output: bool
    max_tirp_length: int
    num_comma: str
    symbol_type: str
    skip_followers: bool
    entity_ids_num: str
    index_same: bool
    semicolon_end: bool
    need_one_sized: bool
    selected_variables: str
    calc_offsets: bool
    print_instances: bool
    print_params: bool
    num_of_entities: int
    filter_overlapping_grad_state: bool
    tirps: list = field(default_factory=list)


@dataclass
class tirp:
    size: int
    symbols: list
    relations: list
    vertical_support: float
    mean_horizontal_support: float
    mean_duration: float
    mean_offset_from_start: float
    mean_offset_from_end: float
    entities: dict = field(default_factory=dict)

    def to_tim_cls0(self):
        stats = tirp_stats(
            self.vertical_support,
            self.mean_horizontal_support,
            self.mean_duration,
            self.mean_offset_from_start,
            self.mean_offset_from_end,
            self.entities,
        )
        return tirp_object(self.size, self.symbols, self.relations, stats, None)

    def to_tim_cls1(self):
        stats = tirp_stats(
            self.vertical_support,
            self.mean_horizontal_support,
            self.mean_duration,
            self.mean_offset_from_start,
            self.mean_offset_from_end,
            self.entities,
        )
        return tirp_object(self.size, self.symbols, self.relations, None, stats)


@dataclass
class instance:
    entity_id: str
    intervals: list
    duration: float
    offset_from_start: float
    offset_from_end: float


@dataclass
class entity:
    id: str
    window_start: float
    window_end: float
    mean_duration: float
    mean_offset_from_start: float
    mean_offset_from_end: float
    instances: list = field(default_factory=list)
