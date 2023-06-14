import math
import statistics
from scipy import stats, mean


class TIRP(object):
    def __init__(
        self,
        size=0,
        symbols=[],
        relations=[],
        num_supporting_entities=0,
        mean_horizontal_support=0,
        supporting_instances=list(),
        mean_of_first_interval=0.0,
        vertical_support=0,
        mean_duration=0,
        supporting_entities_properties={},
        build_supporting_instances=False,
        is_class_0=True,
        mean_offset_from_start=0,
        mean_offset_from_end=0,
        entities_stats={},
    ):
        self.__size = size
        self.__symbols = symbols
        self.__relations = relations
        self.__exist_in_class1 = False
        self.__exist_in_class0 = False

        """class 0 properties"""
        self.__num_supporting_entities_0 = num_supporting_entities if is_class_0 else 0
        self.__mean_horizontal_support_0 = mean_horizontal_support if is_class_0 else 0
        self.__vertical_support_0 = vertical_support if is_class_0 else 0
        self.__mean_duration_0 = round(mean_duration, 2) if is_class_0 else 0
        self.__supporting_instances_0 = supporting_instances if is_class_0 else []
        """average duration of first symbol in TIRP"""
        self.__mean_of_first_interval_0 = mean_of_first_interval if is_class_0 else 0
        """array that every pair of cells: [offset from start of first interval, offset from end of first interval]"""
        self.__mean_offset_from_first_symbol_0 = list()
        self.build_supporting_instances_0 = build_supporting_instances if is_class_0 else False
        self.__symbols_names = []
        self.__mean_offset_from_start = round(mean_offset_from_start, 2)
        self.__mean_offset_from_end = round(mean_offset_from_end, 2)
        self.__supporting_entities_properties = supporting_entities_properties
        self.entities_stats = entities_stats
        self.hs_confidence_interval_low = 0
        self.hs_confidence_interval_high = 0
        self.md_confidence_interval_low = 0
        self.md_confidence_interval_high = 0
        if len(list(entities_stats.keys())) > 0:
            self.calculate_confidence_interval(entities_stats)

        """class 1 properties"""
        self.__num_supporting_entities_1 = 0
        self.__mean_horizontal_support_1 = 0
        self.__vertical_support_1 = 0
        self.__mean_duration_1 = 0
        self.__occurences_1 = []
        self.__supporting_instances_1 = []
        """average duration of first symbol in TIRP"""
        self.__mean_of_first_interval_1 = 0
        """array that every pair of cells: [offset from start of first interval, offset from end of first interval]"""
        self.__mean_offset_from_first_symbol_1 = []
        self.build_supporting_instances_1 = False
        self.__symbols_names = []
        self.__supporting_entities_properties_class_1 = {}
        self.__mean_offset_from_start_class_1 = 0
        self.__mean_offset_from_end_class_1 = 0
        self.entities_stats_class_1 = {}
        self.hs_confidence_interval_low_class_1 = 0
        self.hs_confidence_interval_high_class_1 = 0
        self.md_confidence_interval_low_class_1 = 0
        self.md_confidence_interval_high_class_1 = 0
        self.set_mean_intervals(self.__supporting_instances_0, self.__size)

    def calculate_confidence_interval(self, entities_stats, is_class_1=False):
        hs_per_entity = []
        md_per_entity = []
        for entity in entities_stats.keys():
            hs_per_entity.append(entities_stats[entity][0])
            md_per_entity.append(entities_stats[entity][1])
        mhs = mean(hs_per_entity)
        mmd = mean(md_per_entity)
        num_of_entities_squared = math.sqrt(len(entities_stats.keys()))
        std_deviation_hs = statistics.stdev(hs_per_entity) if len(hs_per_entity) > 1 else 0
        std_deviation_md = statistics.stdev(md_per_entity) if len(md_per_entity) > 1 else 0
        if not is_class_1:
            self.hs_confidence_interval_low = mhs - (
                1.96 * std_deviation_hs / num_of_entities_squared
            )
            self.hs_confidence_interval_high = mhs + (
                1.96 * std_deviation_hs / num_of_entities_squared
            )
            self.md_confidence_interval_low = mmd - (
                1.96 * std_deviation_md / num_of_entities_squared
            )
            self.md_confidence_interval_high = mmd + (
                1.96 * std_deviation_md / num_of_entities_squared
            )
        else:
            self.hs_confidence_interval_low_class_1 = mhs - (
                1.96 * std_deviation_hs / num_of_entities_squared
            )
            self.hs_confidence_interval_high_class_1 = mhs + (
                1.96 * std_deviation_hs / num_of_entities_squared
            )
            self.md_confidence_interval_low_class_1 = mmd - (
                1.96 * std_deviation_md / num_of_entities_squared
            )
            self.md_confidence_interval_high_class_1 = mmd + (
                1.96 * std_deviation_md / num_of_entities_squared
            )

    """iterates over the supporting entities of the tirp and sets metrics related to the TIRP intervals"""

    def set_mean_intervals(self, supporting_instances, tirp_size):
        for instance in supporting_instances:
            duration_of_instance = 0
            mean_offset_from_first_symbol_of_instance = list()
            for symbolic in instance.get_symbolic_intervals():
                j = 0
                end_time_of_first_symbol = symbolic[0].getEndTime()
                for i in range(0, tirp_size):
                    start_time = symbolic[i].getStartTime()
                    end_time = symbolic[i].getEndTime()
                    if i == 0:
                        duration = int(end_time) - int(start_time)
                        # self.__mean_of_first_interval += duration
                        duration_of_instance += duration
                    diff_from_start = int(start_time) - int(end_time_of_first_symbol)
                    diff_from_end = int(end_time) - int(end_time_of_first_symbol)
                    if len(mean_offset_from_first_symbol_of_instance) < j + 1:
                        # self.__mean_offset_from_first_symbol.append(diff_from_start)
                        mean_offset_from_first_symbol_of_instance.append(diff_from_start)
                        mean_offset_from_first_symbol_of_instance.append(diff_from_end)
                        # self.__mean_offset_from_first_symbol.append(diff_from_end)
                    else:
                        mean_offset_from_first_symbol_of_instance[j] += diff_from_start
                        mean_offset_from_first_symbol_of_instance[j + 1] += diff_from_end
                    j = j + 2
            self.__mean_of_first_interval_0 += duration_of_instance / len(
                instance.get_symbolic_intervals()
            )
            for i in range(0, len(mean_offset_from_first_symbol_of_instance)):
                mean_offset_from_first_symbol_of_instance[
                    i
                ] = mean_offset_from_first_symbol_of_instance[i] / len(
                    instance.get_symbolic_intervals()
                )
                if len(self.__mean_offset_from_first_symbol_0) < i + 1:
                    self.__mean_offset_from_first_symbol_0.append(
                        mean_offset_from_first_symbol_of_instance[i]
                    )
                else:
                    self.__mean_offset_from_first_symbol_0[
                        i
                    ] += mean_offset_from_first_symbol_of_instance[i]
        # make it mean
        if len(supporting_instances) > 0:
            # self.__mean_of_first_interval = round(self.__mean_of_first_interval / counter, 2)
            self.__mean_of_first_interval_0 = round(
                self.__mean_of_first_interval_0 / len(supporting_instances), 2
            )
        for i in range(0, len(self.__mean_offset_from_first_symbol_0)):
            # self.__mean_offset_from_first_symbol[i] = round(self.__mean_offset_from_first_symbol[i] / counter, 2)
            self.__mean_offset_from_first_symbol_0[i] = round(
                self.__mean_offset_from_first_symbol_0[i] / len(supporting_instances), 2
            )

    def set_tirp_in_class0(self):
        self.__exist_in_class0 = True

    def set_tirp_in_class1(self):
        self.__exist_in_class1 = True

    """this method is called when a tirp is discovered and exist in class 1"""

    def set_class_1_properties(
        self,
        size,
        symbols,
        relations,
        num_supporting_entities,
        mean_horizontal_support,
        supporting_instances=list(),
        mean_of_first_interval=0.0,
        vertical_support=0,
        mean_duration=0,
        mean_offset_from_first_symbol=list(),
        build_supporting_instances=False,
        supporting_entities_properties={},
        mean_offset_from_start=0,
        mean_offset_from_end=0,
        entities_stats={},
    ):
        self.__size = size
        self.__symbols = symbols
        self.__relations = relations
        self.__num_supporting_entities_1 = num_supporting_entities
        self.__mean_horizontal_support_1 = mean_horizontal_support
        self.__vertical_support_1 = vertical_support
        self.__mean_duration_1 = mean_duration
        self.__supporting_instances_1 = supporting_instances
        self.__mean_of_first_interval_1 = mean_of_first_interval
        self.__mean_offset_from_first_symbol_1 = mean_offset_from_first_symbol
        self.__mean_offset_from_start_class_1 = mean_offset_from_start
        self.__mean_offset_from_end_class_1 = mean_offset_from_end
        self.build_supporting_instances_1 = build_supporting_instances
        mean_first_inter = self.set_supporting_instances(
            supporting_instances=self.__supporting_instances_1,
            build_supporting_instances=self.build_supporting_instances_1,
            mean_of_first_interval=self.__mean_of_first_interval_1,
            mean_offset_from_first_symbol=self.__mean_offset_from_first_symbol_1,
        )

        self.__mean_of_first_interval_1 = mean_first_inter
        self.__supporting_entities_properties_class_1 = supporting_entities_properties
        self.calculate_confidence_interval(entities_stats, True)

    def get_symbols(self):
        return self.__symbols

    def get_size(self):
        return self.__size

    def get_relations(self):
        return self.__relations

    def get_mean_horizontal_support_0(self):
        return self.__mean_horizontal_support_0

    def is_in_class_0(self):
        return int(self.__num_supporting_entities_0) > 0

    def is_in_class_1(self):
        return int(self.__num_supporting_entities_1) > 0

    """gets a list and returns a string (like toString())"""

    def convert_list_to_string(self, list):
        str = ""
        for item in list:
            str = str + " " + item
        return str

    """gets a list of symbols and returns a string (like toString())"""

    def string_symbols(self, symbols):
        str = symbols[0]
        for i in range(1, len(symbols), 1):
            str = str + "-" + symbols[i]
        return str

    """gets a list of relations and returns a string (like toString())"""

    def string_relations(self, relations):
        if len(relations) > 0:
            str = relations[0] + "."
            for i in range(1, len(relations), 1):
                str = str + relations[i] + "."
            return str
        else:
            return ""

    def get_vector_in_size(self, vector_size):
        vector_symbol = []
        sum_relations_till_now = 0
        index_symbol = vector_size
        for index in range(0, index_symbol):
            vector_symbol.append(
                self.__relations[sum_relations_till_now + index_symbol - index - 1]
            )
            sum_relations_till_now += index_symbol - index
        return vector_symbol

    """same as the code in the constructor (in the end of constructor), the difference is that this method is called when the
    TIRP is found in class 1"""

    def set_supporting_instances(
        self,
        supporting_instances,
        build_supporting_instances,
        mean_of_first_interval,
        mean_offset_from_first_symbol,
    ):
        if build_supporting_instances:
            for instance in supporting_instances:
                duration_of_instance = 0
                mean_offset_from_first_symbol_of_instance = list()
                for symbolic in instance.get_symbolic_intervals():
                    j = 0
                    end_time_of_first_symbol = symbolic[0].getEndTime()
                    for i in range(0, self.__size):
                        start_time = symbolic[i].getStartTime()
                        end_time = symbolic[i].getEndTime()
                        if i == 0:
                            duration = int(end_time) - int(start_time)
                            duration_of_instance += duration
                        diff_from_start = int(start_time) - int(end_time_of_first_symbol)
                        diff_from_end = int(end_time) - int(end_time_of_first_symbol)
                        if len(mean_offset_from_first_symbol_of_instance) < j + 1:
                            mean_offset_from_first_symbol_of_instance.append(diff_from_start)
                            mean_offset_from_first_symbol_of_instance.append(diff_from_end)
                        else:
                            mean_offset_from_first_symbol_of_instance[j] += diff_from_start
                            mean_offset_from_first_symbol_of_instance[j + 1] += diff_from_end
                        j = j + 2
                mean_of_first_interval += duration_of_instance / len(
                    instance.get_symbolic_intervals()
                )
                for i in range(0, len(mean_offset_from_first_symbol_of_instance)):
                    mean_offset_from_first_symbol_of_instance[
                        i
                    ] = mean_offset_from_first_symbol_of_instance[i] / len(
                        instance.get_symbolic_intervals()
                    )
                    if len(mean_offset_from_first_symbol) < i + 1:
                        mean_offset_from_first_symbol.append(
                            mean_offset_from_first_symbol_of_instance[i]
                        )
                    else:
                        mean_offset_from_first_symbol[
                            i
                        ] += mean_offset_from_first_symbol_of_instance[i]
            # make it mean
            if len(supporting_instances) > 0:
                mean_of_first_interval = round(
                    mean_of_first_interval / len(supporting_instances), 2
                )
            for i in range(0, len(mean_offset_from_first_symbol)):
                mean_offset_from_first_symbol[i] = round(
                    mean_offset_from_first_symbol[i] / len(supporting_instances), 2
                )
        return mean_of_first_interval

    def set_symbols_names(self, symbols_names):
        self.__symbols_names = symbols_names

    def get_symbols_names(self):
        return self.__symbols_names

    """gets a list of objects and serializes them into an array of jsons"""

    def get_json_from_field(self, list_instances):
        result = []
        for instance in list_instances:
            result.append(instance.serialize())
        return result

    """serielizing the properties of supporting entities to a json"""

    def convert_entities_properties(self, properties):
        if len(list(properties.keys())) == 0:
            return properties
        entities_properties = {}
        entity_id = list(properties.keys())[0]
        keys = properties[entity_id].keys()
        for key in keys:
            entities_properties[key] = []
        for entity in properties.keys():
            entity_json = properties[entity]
            for prop, val in entity_json.items():
                jsons_arr = entities_properties[prop]
                if val not in [list(j.keys())[0] for j in jsons_arr]:
                    entities_properties[prop].append({val: 1})
                else:
                    for i in range(len(jsons_arr)):
                        if list(jsons_arr[i].keys())[0] == val:
                            entities_properties[prop][i][val] += 1
        return entities_properties

    """converts the TIRP object to a serialized json to write to a text file"""

    def serialize(self):
        return {
            "size": self.__size,
            "symbols": self.__symbols,
            "symbols_names": self.__symbols_names,
            "relations": self.__relations,
            "exist_in_class0": self.__exist_in_class0,
            "exist_in_class1": self.__exist_in_class1,
            "num_supporting_entities_0": self.__num_supporting_entities_0,
            "num_supporting_entities_1": self.__num_supporting_entities_1,
            "mean_horizontal_support_0": self.__mean_horizontal_support_0,
            "mean_horizontal_support_1": self.__mean_horizontal_support_1,
            "vertical_support_0": self.__vertical_support_0,
            "vertical_support_1": self.__vertical_support_1,
            "mean_duration_0": self.__mean_duration_0,
            "mean_duration_1": self.__mean_duration_1,
            "mean_of_first_interval_0": self.__mean_of_first_interval_0,
            "mean_of_first_interval_1": self.__mean_of_first_interval_1,
            "mean_offset_from_first_symbol_0": self.__mean_offset_from_first_symbol_0,
            "mean_offset_from_first_symbol_1": self.__mean_offset_from_first_symbol_1,
            "build_supporting_instances_0": False,
            "build_supporting_instances_1": False,
            "supporting_entities_properties_0": self.convert_entities_properties(
                self.__supporting_entities_properties
            ),
            "supporting_entities_properties_1": self.convert_entities_properties(
                self.__supporting_entities_properties_class_1
            ),
            "md_confidence_interval_low": self.md_confidence_interval_low,
            "md_confidence_interval_low_class_1": self.md_confidence_interval_low_class_1,
            "md_confidence_interval_high": self.md_confidence_interval_high,
            "md_confidence_interval_high_class_1": self.md_confidence_interval_high_class_1,
            "hs_confidence_interval_low": self.hs_confidence_interval_low,
            "hs_confidence_interval_low_class_1": self.hs_confidence_interval_low_class_1,
            "hs_confidence_interval_high": self.hs_confidence_interval_high,
            "hs_confidence_interval_high_class_1": self.hs_confidence_interval_high_class_1,
        }
