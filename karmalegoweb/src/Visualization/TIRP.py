import json
import math
import statistics
from collections import Counter

from scipy import stats
from scipy import mean

from karmalegoweb.src.Visualization.SupportingInstance import SupportingInstance


class TIRP(object):
    def __init__(
        self,
        tirp_size=0,
        symbols=list(),
        relation=list(),
        supporting_instances=list(),
        supporting_entities=list(),
        vertical_support=0,
        mean_horizontal_support=0,
        mean_duration=0,
        mean_offset_from_start=0,
        mean_offset_from_end=0,
        path=None,
        min_vertical_support=0,
    ):
        if tirp_size == -1:
            return

        self.__tirp_size: int = tirp_size
        self.__symbols: list = symbols
        self.__rel: list = relation
        self.__supporting_instances: list = supporting_instances
        self.__supporting_entities: list = supporting_entities
        self.__vertical_support: int = vertical_support
        self.__mean_horizontal_support: float = round(mean_horizontal_support, 2)
        self.__mean_duration: float = round(mean_duration, 2)
        self.__mean_offset_from_start: float = round(mean_offset_from_start, 2)
        self.__mean_offset_from_end: float = round(mean_offset_from_end, 2)
        self.__mean_of_first_interval: float = 0.0
        self.__mean_offset_from_first_symbol = list()
        self.__childes = list()
        self.__unique_name = self.get_unique_name()
        self.__supporting_entities_properties = self.parse_entities(
            path=path, ids=self.__supporting_entities
        )
        self.__hs_confidence_interval_low_class_0: float = 0
        self.__hs_confidence_interval_high_class_0: float = 0
        self.__md_confidence_interval_low_class_0: float = 0
        self.__md_confidence_interval_high_class_0: float = 0
        self.__exist_in_class1 = False
        self.__exist_in_class0 = False
        self.__vertical_support_class_1: float = 0
        self.__mean_horizontal_support_class_1: float = 0.0
        self.__p_value_mhs: float = 0
        self.__mean_duration_class_1: float = 0.0
        self.__p_value_md: float = 0
        self.__mean_offset_from_start_class_1: float = 0
        self.__mean_offset_from_end_class_1: float = 0
        self.__mean_of_first_interval_class_1: float = 0
        self.__mean_offset_from_first_symbol_class_1: float = list()
        self.__supporting_entities_properties_class_1 = dict()
        self.__hs_confidence_interval_low_class_1: float = 0
        self.__hs_confidence_interval_high_class_1: float = 0
        self.__md_confidence_interval_low_class_1: float = 0
        self.__md_confidence_interval_high_class_1: float = 0

        # counter = 0;
        for instance in supporting_instances:
            duration_of_instance = 0
            mean_offset_from_first_symbol_of_instance = list()
            for symbolic in instance.get_symbolic_intervals():
                j = 0
                # counter = counter + 1
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
            self.__mean_of_first_interval += duration_of_instance / len(
                instance.get_symbolic_intervals()
            )
            for i in range(0, len(mean_offset_from_first_symbol_of_instance)):
                mean_offset_from_first_symbol_of_instance[
                    i
                ] = mean_offset_from_first_symbol_of_instance[i] / len(
                    instance.get_symbolic_intervals()
                )
                if len(self.__mean_offset_from_first_symbol) < i + 1:
                    self.__mean_offset_from_first_symbol.append(
                        mean_offset_from_first_symbol_of_instance[i]
                    )
                else:
                    self.__mean_offset_from_first_symbol[
                        i
                    ] += mean_offset_from_first_symbol_of_instance[i]
        # make it mean
        if len(supporting_instances) > 0:
            # self.__mean_of_first_interval = round(self.__mean_of_first_interval / counter, 2)
            self.__mean_of_first_interval = round(
                self.__mean_of_first_interval / len(supporting_instances), 2
            )
        for i in range(0, len(self.__mean_offset_from_first_symbol)):
            # self.__mean_offset_from_first_symbol[i] = round(self.__mean_offset_from_first_symbol[i] / counter, 2)
            self.__mean_offset_from_first_symbol[i] = round(
                self.__mean_offset_from_first_symbol[i] / len(supporting_instances), 2
            )

        if len(self.__supporting_instances) > 1:
            hs_class_0 = list()
            md_class_0 = list()
            for instance in self.__supporting_instances:
                hs_class_0.append(len(instance.get_symbolic_intervals()))
                md_class_0.append(instance.get_mean_duration())
            self.__hs_confidence_interval_low_class_0 = mean(hs_class_0) - (
                1.96 * statistics.stdev(hs_class_0) / math.sqrt(len(hs_class_0))
            )
            self.__hs_confidence_interval_high_class_0 = mean(hs_class_0) + (
                1.96 * statistics.stdev(hs_class_0) / math.sqrt(len(hs_class_0))
            )
            self.__md_confidence_interval_low_class_0 = mean(md_class_0) - (
                1.96 * statistics.stdev(md_class_0) / math.sqrt(len(md_class_0))
            )
            self.__md_confidence_interval_high_class_0 = mean(md_class_0) + (
                1.96 * statistics.stdev(md_class_0) / math.sqrt(len(md_class_0))
            )

    def get_tirp_size(self) -> int:
        return self.__tirp_size

    def get_rel_size(self) -> int:
        return len(self.__rel)

    def get_vertical_support(self) -> int:
        return self.__vertical_support

    def get_vertical_support_class_1(self) -> int:
        return self.__vertical_support_class_1

    def get_supporting_instances(self):
        return self.__supporting_instances

    def set_supporting_instances(self, supporting_instances):
        self.__supporting_instances = supporting_instances

    def set_supporting_entitie(self, supporting_entitie):
        self.__supporting_entities = supporting_entitie

    def get_unique_name(self):
        TIRP_name = ""
        for symbol in self.__symbols:
            TIRP_name += symbol + "-"
        TIRP_name += ","
        for rel in self.__rel:
            TIRP_name += rel + "."
        return TIRP_name

    def get_symbols(self):
        return self.__symbols

    def get_rels(self):
        return self.__rel

    def get_childes(self):
        return self.__childes

    def get_vs(self):
        return self.__vertical_support

    def get_mhs(self):
        return self.__mean_horizontal_support

    def get_mmd(self):
        return self.__mean_duration

    def get_mmd_class1(self):
        return self.__mean_duration_class_1

    def get_mhs_class1(self):
        return self.__mean_horizontal_support_class_1

    def get_vs_class1(self):
        return self.__vertical_support_class_1

    def get_mean_of_first_interval(self):
        return self.__mean_of_first_interval

    def get_mean_of_first_interval_class_1(self):
        return self.__mean_of_first_interval_class_1

    def get_mean_offset_from_first_symbol(self):
        return self.__mean_offset_from_first_symbol

    def get_mean_offset_from_first_symbol_class_1(self):
        return self.__mean_offset_from_first_symbol_class_1

    def get_p_value_md(self):
        return self.__p_value_md

    def get_p_value_mhs(self):
        return self.__p_value_mhs

    def get_exist_in_class1(self):
        return self.__exist_in_class1

    def set_exist_in_class_1(self):
        self.__exist_in_class1 = True

    def get_exist_in_class_0(self):
        return self.__exist_in_class0

    def set_exist_in_class_0(self):
        self.__exist_in_class0 = True

    def update_childs(self, childs):
        self.__childes = childs

    def make_child_truthy(self):
        if len(self.__childes) > 0 and self.__childes[0]:
            self.__childes = [True]

    def set_exists(self, min_vertical_support, num_of_entities, num_of_entities_class_1):
        self.__exist_in_class0 = self.__vertical_support / num_of_entities >= min_vertical_support
        self.__exist_in_class1 = (
            self.__vertical_support_class_1 / num_of_entities_class_1 >= min_vertical_support
        )

    def set_childes(self, TIRPs_in_output_file=None, has_childs=None):
        """
        This method finds the TIRP's immediate childes and adds them to the childes list property of the TIRP
        :param TIRPs_in_output_file: The file that contains all the TIRPs that start with the first symbol
        :param has_childs: for root elements that have childs
        :return:
        """
        if has_childs:
            self.__childes.append(True)
        elif TIRPs_in_output_file:
            self.__childes.clear()
            for TIRP_element in TIRPs_in_output_file:
                if TIRP_element.get_tirp_size() == self.__tirp_size + 1 and self.__tirp_size == 1:
                    self.__childes.append(TIRP_element)
                    TIRP_element.set_childes(TIRPs_in_output_file)
                elif TIRP_element.get_tirp_size() == self.__tirp_size + 1:
                    # if TIRP_element.get_symbols() == ["Albumin_FULL.Low", "Glucose_FULL.Low", "Glucose_FULL.Low"] and self.get_symbols() == ["Albumin_FULL.Low", "Glucose_FULL.Low"] :
                    #     if self.__tirp_size == 3:
                    #         a = 2
                    is_match = True
                    for i in range(0, len(self.get_symbols())):
                        if self.__symbols[i] != TIRP_element.get_symbols()[i]:
                            is_match = False
                            break
                    if is_match:
                        num_of_symbols = len(self.get_symbols())
                        num_of_rels = int(num_of_symbols * (num_of_symbols - 1) / 2)
                        for i in range(0, num_of_rels):
                            if self.__rel[i] != TIRP_element.get_rels()[i]:
                                is_match = False
                                break
                        if is_match:
                            self.__childes.append(TIRP_element)
                            TIRP_element.set_childes(TIRPs_in_output_file)

    def parse_entities(self, path, ids):
        res = dict()
        if not path:
            return res
        try:
            with open(path + "/entities.json") as f:
                lines = f.readlines()
                j = []
                for line in lines:
                    j.append(json.loads(line))
                # j = json.load(f)
                c = Counter()
                for d in j:
                    for k, v in d.items():
                        key = k.rstrip()
                        val = v.rstrip()
                        if key == "id":
                            continue
                        if d["id"] in ids:
                            c.update([key + "-" + val])
                        l = res.get(key)
                        if l:
                            if val not in l:
                                res[key].append(val)
                        else:
                            res[key] = list()
                            res[key].append(val)
                for k in res.keys():
                    v = res[k].copy()
                    res[k].clear()
                    for prop in v:
                        prop_dict = dict()
                        prop_name = k + "-" + prop
                        if prop_name in c.keys():
                            prop_dict[prop] = c[prop_name]
                        else:
                            prop_dict[prop] = 0
                        res[k].append(prop_dict)
                return res
        except:
            return res

    def set_class_1_properties(self, class_1_tirp):

        self.__exist_in_class1 = True
        self.__vertical_support_class_1 = class_1_tirp.__vertical_support
        self.__mean_horizontal_support_class_1 = class_1_tirp.__mean_horizontal_support
        hs_class_0 = list()
        md_class_0 = list()
        hs_class_1 = list()
        md_class_1 = list()
        for instance in self.__supporting_instances:
            hs_class_0.append(len(instance.get_symbolic_intervals()))
            md_class_0.append(instance.get_mean_duration())
        for instance in class_1_tirp.get_supporting_instances():
            instance_obj = SupportingInstance()
            instance_obj.__dict__.clear()
            instance_obj.__dict__.update(instance)
            hs_class_1.append(len(instance_obj.get_symbolic_intervals()))
            md_class_1.append(instance_obj.get_mean_duration())
        t, p_hs = stats.ttest_ind(hs_class_0, hs_class_1, equal_var=False)
        if math.isnan(p_hs):
            p_hs = 1
        # else:
        #     p_hs *= 10
        # if p_hs < 0.05:

        self.__p_value_mhs = p_hs
        self.__mean_duration_class_1 = class_1_tirp.__mean_duration
        t, p_md = stats.ttest_ind(md_class_0, md_class_1, equal_var=False)
        if math.isnan(p_md):
            p_md = 1
        # else:
        #     p_md *= 10
        self.__p_value_md = p_md
        self.__mean_offset_from_start_class_1 = class_1_tirp.__mean_offset_from_start
        self.__mean_offset_from_end_class_1 = class_1_tirp.__mean_offset_from_end
        self.__mean_of_first_interval_class_1 = class_1_tirp.__mean_of_first_interval
        self.__mean_offset_from_first_symbol_class_1 = class_1_tirp.__mean_offset_from_first_symbol
        self.__supporting_entities_properties_class_1 = (
            class_1_tirp.__supporting_entities_properties
        )

        # self.__mean_horizontal_support = 0 if math.isnan(mhs0) else mhs0
        # self.__mean_horizontal_support_class_1 = 0 if math.isnan(mhs1) else mhs1
        # self.__mean_horizontal_support_class_0 = 0 if math.isnan(mhs0) else mhs0

        mhs1 = mean(hs_class_1)
        md1 = mean(md_class_1)

        self.__hs_confidence_interval_low_class_1 = mhs1 - 1.96 * statistics.stdev(
            hs_class_1
        ) / math.sqrt(len(hs_class_1))
        self.__hs_confidence_interval_high_class_1 = mhs1 + 1.96 * statistics.stdev(
            hs_class_1
        ) / math.sqrt(len(hs_class_1))
        self.__md_confidence_interval_low_class_1 = md1 - 1.96 * statistics.stdev(
            md_class_1
        ) / math.sqrt(len(md_class_1))
        self.__md_confidence_interval_high_class_1 = md1 + 1.96 * statistics.stdev(
            md_class_1
        ) / math.sqrt(len(md_class_1))

    def equals(self, class_1_tirp):
        if self.get_symbols() == class_1_tirp.get_symbols():
            if self.get_rels() == class_1_tirp.get_rels():
                return True
        return False

    def set_class_0_properties(self, min_vertical_support):
        self.__vertical_support_class_1 = self.__vertical_support
        self.__vertical_support = 0
        self.__mean_horizontal_support_class_1 = self.__mean_horizontal_support
        self.__mean_horizontal_support = 0
        self.__mean_duration_class_1 = self.__mean_duration
        self.__mean_duration = 0
        self.__supporting_entities_properties_class_1 = self.__supporting_entities_properties
        self.__supporting_entities_properties = list()
        self.__hs_confidence_interval_low_class_1 = self.__hs_confidence_interval_low_class_0
        self.__hs_confidence_interval_low_class_0 = 0
        self.__hs_confidence_interval_high_class_1 = self.__hs_confidence_interval_high_class_0
        self.__hs_confidence_interval_high_class_0 = 0
        self.__md_confidence_interval_low_class_1 = self.__md_confidence_interval_low_class_0
        self.__md_confidence_interval_low_class_0 = 0
        self.__md_confidence_interval_high_class_1 = self.__md_confidence_interval_high_class_0
        self.__md_confidence_interval_high_class_0 = 0

    def full_init(
        self,
        tirp_size,
        symbols,
        relations,
        supporting_instances,
        supporting_entities,
        vertical_support,
        mean_horizontal_support,
        mean_duration,
        mean_offset_from_start,
        mean_offset_from_end,
        mean_of_first_interval,
        mean_offset_from_symbol,
        children,
        unique_name,
        supporting_entities_properties,
        hs_confidence_interval_low_class_0,
        hs_confidence_interval_high_class_0,
        md_confidence_interval_low_class_0,
        md_confidence_interval_high_class_0,
        exist_in_class1,
        exist_in_class0,
        vertical_support_class_1,
        mean_horizontal_support_class_1,
        p_value_mhs,
        mean_duration_class_1,
        p_value_md,
        mean_offset_from_start_class_1,
        mean_offset_from_end_class_1,
        mean_of_first_interval_class_1,
        mean_offset_from_first_symbol_class_1,
        supporting_entities_properties_class_1,
        hs_confidence_interval_low_class_1,
        hs_confidence_interval_high_class_1,
        md_confidence_interval_low_class_1,
        md_confidence_interval_high_class_1,
    ):
        self.__tirp_size: int = tirp_size
        self.__symbols: list = symbols
        self.__rel: list = relations
        self.__supporting_instances: list = supporting_instances
        self.__supporting_entities: list = supporting_entities
        self.__vertical_support: int = vertical_support
        self.__mean_horizontal_support: float = mean_horizontal_support
        self.__mean_duration: float = mean_duration
        self.__mean_offset_from_start: float = mean_offset_from_start
        self.__mean_offset_from_end: float = mean_offset_from_end
        self.__mean_of_first_interval: float = mean_of_first_interval
        self.__mean_offset_from_first_symbol = mean_offset_from_symbol
        self.__childes = children
        self.__unique_name = unique_name
        self.__supporting_entities_properties = supporting_entities_properties
        self.__hs_confidence_interval_low_class_0: float = hs_confidence_interval_low_class_0
        self.__hs_confidence_interval_high_class_0: float = hs_confidence_interval_high_class_0
        self.__md_confidence_interval_low_class_0: float = md_confidence_interval_low_class_0
        self.__md_confidence_interval_high_class_0: float = md_confidence_interval_high_class_0
        self.__exist_in_class1 = exist_in_class1
        self.__exist_in_class0 = exist_in_class0
        self.__vertical_support_class_1: float = vertical_support_class_1
        self.__mean_horizontal_support_class_1: float = mean_horizontal_support_class_1
        self.__p_value_mhs: float = p_value_mhs
        self.__mean_duration_class_1: float = mean_duration_class_1
        self.__p_value_md: float = p_value_md
        self.__mean_offset_from_start_class_1: float = mean_offset_from_start_class_1
        self.__mean_offset_from_end_class_1: float = mean_offset_from_end_class_1
        self.__mean_of_first_interval_class_1: float = mean_of_first_interval_class_1
        self.__mean_offset_from_first_symbol_class_1: float = mean_offset_from_first_symbol_class_1
        self.__supporting_entities_properties_class_1 = supporting_entities_properties_class_1
        self.__hs_confidence_interval_low_class_1: float = hs_confidence_interval_low_class_1
        self.__hs_confidence_interval_high_class_1: float = hs_confidence_interval_high_class_1
        self.__md_confidence_interval_low_class_1: float = md_confidence_interval_low_class_1
        self.__md_confidence_interval_high_class_1: float = md_confidence_interval_high_class_1
