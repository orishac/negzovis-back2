from dataclasses import dataclass, field
import math
import statistics
from scipy import stats, mean
from sqlalchemy import true
from karmalegoweb.src.Visualization.SupportingInstance import SupportingInstance

from karmalegoweb.src.Visualization.TIRP import TIRP as old_tip


@dataclass
class tirp_stats:
    vertical_support: float
    mean_horizontal_support: float
    mean_mean_duration: float
    mean_offset_from_start: float
    mean_offset_from_end: float

    entities: dict = field(default_factory=dict)

    mean_duration_of_first_interval: float = None
    mean_offset_from_first_symbol: list = None
    hs_confidence_interval_high: float = None
    hs_confidence_interval_low: float = None
    md_confidence_interval_high: float = None
    md_confidence_interval_low: float = None
    supporting_entities_properties: dict = None

    def calculate_extensions(self, tirp_size, entities):
        self.__calculate_confidence_interval()
        self.__calculate_mean_first_interval_duration()
        self.__calculate_mean_offset_from_first_symbol(tirp_size)
        self.__calculate_entities_properties(entities)

    def __calculate_entities_properties(self, entities):
        if entities is None:
            self.supporting_entities_properties = {}
            return

        entity = entities[0]
        properties = {}
        for property in entity:
            if property != "id":
                properties[property] = {}

        entities = {entity["id"]: entity for entity in entities}
        for entity_id in self.entities:
            for property, value in entities[entity_id].items():
                if property != "id":
                    if value not in properties[property]:
                        properties[property][value] = 0
                    properties[property][value] += 1

        self.supporting_entities_properties = properties

    def __calculate_mean_first_interval_duration(self):
        vs = len(self.entities)

        mean_first_interval_duration = 0
        for entity in self.entities.values():
            mean_entity_first_interval_duration = 0
            for instance in entity.instances:
                start_time, end_time = instance.intervals[0]
                mean_entity_first_interval_duration += end_time - start_time
            mean_first_interval_duration += mean_entity_first_interval_duration / len(
                entity.instances
            )
        self.mean_duration_of_first_interval = round(mean_first_interval_duration / vs, 2)

    def __calculate_mean_offset_from_first_symbol(self, tirp_size):
        """
        Creates an array of the mean offset of the tirp's interval from the end of the first symbold
        For index i, array[2*i] is the mean offset of the end of the first symbol from the start of the i'th symbol
        For index i, array[2*i+1] is the mean offset of the end of the first symbol from the end of the i'th symbol
        """
        vs = len(self.entities)

        mean_mean_offset_from_first_symbol = [0] * 2 * tirp_size

        for entity in self.entities.values():

            mean_offset_first_symbol_start = [0] * tirp_size
            mean_offset_first_symbol_end = [0] * tirp_size

            # Calculating the mean offsets of the current entity
            for instance in entity.instances:
                _, end_time_of_first_symbol = instance.intervals[0]
                for i in range(tirp_size):
                    start_time, end_time = instance.intervals[i]
                    offset_from_start = start_time - end_time_of_first_symbol
                    offset_from_end = end_time - end_time_of_first_symbol
                    mean_offset_first_symbol_start[i] += offset_from_start
                    mean_offset_first_symbol_end[i] += offset_from_end

            hs = len(entity.instances)
            for i in range(tirp_size):
                mean_mean_offset_from_first_symbol[2 * i] += mean_offset_first_symbol_start[i] / hs
                mean_mean_offset_from_first_symbol[2 * i + 1] += (
                    mean_offset_first_symbol_end[i] / hs
                )

        self.mean_offset_from_first_symbol = [
            round(offset / vs, 2) for offset in mean_mean_offset_from_first_symbol
        ]

    def __calculate_confidence_interval(self):
        hs_per_entity = []
        md_per_entity = []
        for entity in self.entities.values():
            hs_per_entity.append(len(entity.instances))
            md_per_entity.append(entity.mean_duration)
        mhs = mean(hs_per_entity)
        mmd = mean(md_per_entity)
        num_of_entities_squared = math.sqrt(len(self.entities))
        std_deviation_hs = statistics.stdev(hs_per_entity) if len(hs_per_entity) > 1 else 0
        std_deviation_md = statistics.stdev(md_per_entity) if len(md_per_entity) > 1 else 0

        self.hs_confidence_interval_low = mhs - (1.96 * std_deviation_hs / num_of_entities_squared)
        self.hs_confidence_interval_high = mhs + (1.96 * std_deviation_hs / num_of_entities_squared)
        self.md_confidence_interval_low = mmd - (1.96 * std_deviation_md / num_of_entities_squared)
        self.md_confidence_interval_high = mmd + (1.96 * std_deviation_md / num_of_entities_squared)


@dataclass
class tirp:
    size: int
    symbols: list
    relations: list
    stats_cls0: tirp_stats = None
    stats_cls1: tirp_stats = None
    children: list = field(default_factory=list)
    has_children: bool = False

    p_value_mhs: float = None
    p_value_md: float = None

    def from_json(self, json):
        self.__dict__.clear()
        self.__dict__.update(json)
        if json["stats_cls0"] is not None:
            self.stats_cls0 = tirp_stats(None, None, None, None, None)
            self.stats_cls0.__dict__.clear()
            self.stats_cls0.__dict__.update(json["stats_cls0"])
        if json["stats_cls1"] is not None:
            self.stats_cls1 = tirp_stats(None, None, None, None, None)
            self.stats_cls1.__dict__.clear()
            self.stats_cls1.__dict__.update(json["stats_cls1"])
        self.children = []
        for child_json in json["children"]:
            child_obj = tirp(None, None, None)
            child_obj.from_json(child_json)
            self.children.append(child_obj)

    def remove_entities(self):
        if self.stats_cls0 is not None:
            self.stats_cls0.entities = {}
        if self.stats_cls1 is not None:
            self.stats_cls1.entities = {}
        for child in self.children:
            child.remove_entities()

    def equal(self, other):
        return (
            self.size == other.size
            and self.symbols == other.symbols
            and self.relations == other.relations
        )

    def calculate_extensions(self, entities):
        self.__calculate_p_values()
        if self.stats_cls0 is not None:
            self.stats_cls0.calculate_extensions(self.size, entities)
        if self.stats_cls1 is not None:
            self.stats_cls1.calculate_extensions(self.size, entities)
        for child in self.children:
            child.calculate_extensions(entities)

    def __calculate_p_values(self):
        if self.stats_cls0 is not None:
            hs_list_cls0 = [len(entity.instances) for entity in self.stats_cls0.entities.values()]
            md_list_cls0 = [entity.mean_duration for entity in self.stats_cls0.entities.values()]
        else:
            hs_list_cls0 = []
            md_list_cls0 = []

        if self.stats_cls1 is not None:
            hs_list_cls1 = [len(entity.instances) for entity in self.stats_cls1.entities.values()]
            md_list_cls1 = [entity.mean_duration for entity in self.stats_cls1.entities.values()]
        else:
            hs_list_cls1 = []
            md_list_cls1 = []

        _, self.p_value_mhs = stats.ttest_ind(hs_list_cls0, hs_list_cls1, equal_var=False)
        _, self.p_value_md = stats.ttest_ind(md_list_cls0, md_list_cls1, equal_var=False)

        if math.isnan(self.p_value_mhs):
            self.p_value_mhs = 1
        if math.isnan(self.p_value_md):
            self.p_value_md = 1

    def to_old_tirp(self, states):
        relations_dict = {
            "<": "before",
            "m": "meets",
            "o": "overlaps",
            "f": "finished by",
            "c": "contains",
            "=": "equals",
            "s": "starts",
            "-": 7,
        }

        children = [child.to_old_tirp(states) for child in self.children]
        if len(children) == 0 and self.has_children:
            children = [True]

        old_tirp_view = old_tip(-1)
        entities_ids_cls0 = (
            list(self.stats_cls0.entities.keys()) if self.stats_cls0 is not None else []
        )
        entities_ids_cls1 = (
            list(self.stats_cls1.entities.keys()) if self.stats_cls1 is not None else []
        )
        supporting_entities = entities_ids_cls0 + entities_ids_cls1

        def entities_to_old_entities(entities):
            supporting_instances = []
            for entity in entities:
                old_entity_view = SupportingInstance(-1)
                symbolic_intervals = []
                for instance in entity.instances:
                    for (index, (start_time, end_time)) in enumerate(instance.intervals):
                        symbolic_interval = {
                            "_start_time": start_time,
                            "_end_time": end_time,
                            "_symbol": states[self.symbols[index]],
                            "_var_id": None,
                        }
                        symbolic_intervals.append(symbolic_interval)

                old_entity_view.full_init(
                    entityId=entity.id,
                    mean_duration=entity.mean_duration,
                    mean_offset_from_end=entity.mean_offset_from_end,
                    mean_offset_from_start=entity.mean_offset_from_start,
                    mean_of_first_interval=0,
                    mean_offset_from_first_symbol=0,
                    symbolic_intervals=symbolic_intervals,
                )
                old_entity_view.set_means()

                supporting_instances.append(old_entity_view)
            return supporting_instances

        supporting_instances_cls0 = (
            entities_to_old_entities(self.stats_cls0.entities.values())
            if self.stats_cls0 is not None
            else []
        )
        supporting_instances_cls1 = (
            entities_to_old_entities(self.stats_cls1.entities.values())
            if self.stats_cls1 is not None
            else []
        )
        supporting_instances = supporting_instances_cls0 + supporting_instances_cls1

        old_tirp_view.full_init(
            tirp_size=self.size,
            symbols=[states[symbol] for symbol in self.symbols],
            relations=[relations_dict[relation] for relation in self.relations],
            p_value_md=self.p_value_md,
            p_value_mhs=self.p_value_mhs,
            exist_in_class0=self.stats_cls0 is not None,
            exist_in_class1=self.stats_cls1 is not None,
            vertical_support=self.stats_cls0.vertical_support if self.stats_cls0 is not None else 0,
            hs_confidence_interval_high_class_0=self.stats_cls0.hs_confidence_interval_high
            if self.stats_cls0 is not None
            else 0,
            hs_confidence_interval_low_class_0=self.stats_cls0.hs_confidence_interval_low
            if self.stats_cls0 is not None
            else 0,
            md_confidence_interval_high_class_0=self.stats_cls0.md_confidence_interval_high
            if self.stats_cls0 is not None
            else 0,
            md_confidence_interval_low_class_0=self.stats_cls0.md_confidence_interval_low
            if self.stats_cls0 is not None
            else 0,
            mean_duration=self.stats_cls0.mean_mean_duration if self.stats_cls0 is not None else 0,
            mean_horizontal_support=self.stats_cls0.mean_horizontal_support
            if self.stats_cls0 is not None
            else 0,
            mean_offset_from_end=self.stats_cls0.mean_offset_from_end
            if self.stats_cls0 is not None
            else 0,
            mean_offset_from_start=self.stats_cls0.mean_offset_from_start
            if self.stats_cls0 is not None
            else 0,
            mean_of_first_interval=self.stats_cls0.mean_duration_of_first_interval
            if self.stats_cls0 is not None
            else 0,
            mean_offset_from_symbol=self.stats_cls0.mean_offset_from_first_symbol
            if self.stats_cls0 is not None
            else 0,
            supporting_entities_properties=self.stats_cls0.supporting_entities_properties
            if self.stats_cls0 is not None
            else {},
            hs_confidence_interval_high_class_1=self.stats_cls1.hs_confidence_interval_high
            if self.stats_cls1 is not None
            else 0,
            hs_confidence_interval_low_class_1=self.stats_cls1.hs_confidence_interval_low
            if self.stats_cls1 is not None
            else 0,
            md_confidence_interval_high_class_1=self.stats_cls1.md_confidence_interval_high
            if self.stats_cls1 is not None
            else 0,
            md_confidence_interval_low_class_1=self.stats_cls1.md_confidence_interval_low
            if self.stats_cls1 is not None
            else 0,
            mean_duration_class_1=self.stats_cls1.mean_mean_duration
            if self.stats_cls1 is not None
            else 0,
            mean_horizontal_support_class_1=self.stats_cls1.mean_horizontal_support
            if self.stats_cls1 is not None
            else 0,
            mean_of_first_interval_class_1=self.stats_cls1.mean_duration_of_first_interval
            if self.stats_cls1 is not None
            else 0,
            mean_offset_from_end_class_1=self.stats_cls1.mean_offset_from_end
            if self.stats_cls1 is not None
            else 0,
            mean_offset_from_first_symbol_class_1=self.stats_cls1.mean_offset_from_first_symbol
            if self.stats_cls1 is not None
            else 0,
            mean_offset_from_start_class_1=self.stats_cls1.mean_offset_from_start
            if self.stats_cls1 is not None
            else 0,
            vertical_support_class_1=self.stats_cls1.vertical_support
            if self.stats_cls1 is not None
            else 0,
            supporting_entities_properties_class_1=self.stats_cls1.supporting_entities_properties
            if self.stats_cls1 is not None
            else {},
            unique_name="-".join(self.symbols) + "|" + ".".join(self.relations),
            supporting_entities=supporting_entities,
            children=children,
            supporting_instances=supporting_instances,
        )

        return old_tirp_view
