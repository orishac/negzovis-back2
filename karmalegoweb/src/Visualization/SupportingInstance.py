class SupportingInstance(object):
    def __init__(
        self,
        entityId=None,
        symbolic_intervals=list(),
        mean_duration=0,
        mean_offset_from_start=0,
        mean_offset_from_end=0,
    ):
        if entityId == -1:
            return
        self.__entityId: str = entityId  ##############
        # self.__duration: float = duration
        # self.__offset_from_start: float = offset_from_start
        # self.__offset_from_end: float = offset_from_end
        self.__symbolic_intervals = list()
        for item in symbolic_intervals:
            self.__symbolic_intervals.append(item)
        # self.__symbolic_intervals = symbolic_intervals
        # self.__mean_of_each_interval: list = mean_of_each_interval
        self.__mean_of_first_interval = 0
        self.__mean_offset_from_first_symbol = list()
        self.__mean_duration: float = round(mean_duration, 2)
        self.__mean_offset_from_start: float = round(mean_offset_from_start, 2)
        self.__mean_offset_from_end: float = round(mean_offset_from_end, 2)

    def set_means(self):
        for symbolic in self.__symbolic_intervals:
            j = 0
            end_time_of_first_symbol = symbolic[0].getEndTime()
            for i in range(0, len(symbolic)):
                start_time = symbolic[i].getStartTime()
                end_time = symbolic[i].getEndTime()
                if i == 0:
                    duration = int(end_time) - int(start_time) + 1
                    self.__mean_of_first_interval += duration
                diff_from_start = int(start_time) - int(end_time_of_first_symbol)
                diff_from_end = int(end_time) - int(end_time_of_first_symbol)
                if len(self.__mean_offset_from_first_symbol) < j + 1:
                    self.__mean_offset_from_first_symbol.append(diff_from_start)
                    self.__mean_offset_from_first_symbol.append(diff_from_end)
                else:
                    self.__mean_offset_from_first_symbol[j] += diff_from_start
                    self.__mean_offset_from_first_symbol[j + 1] += diff_from_end
                j = j + 2
        # make it mean
        if len(self.__symbolic_intervals) > 0:
            self.__mean_of_first_interval = round(
                self.__mean_of_first_interval / len(self.__symbolic_intervals), 2
            )
        for i in range(0, len(self.__mean_offset_from_first_symbol)):
            self.__mean_offset_from_first_symbol[i] = round(
                self.__mean_offset_from_first_symbol[i] / len(self.__symbolic_intervals), 2
            )

    def add_list_to_intervals(self, symbolic_list):
        for item in symbolic_list:
            self.__symbolic_intervals.append(item)

    def get_symbolic_intervals(self):
        return self.__symbolic_intervals

    def get_mean_duration(self):
        return self.__mean_duration

    def get_json_from_field(self, list_instances):
        result = []
        for instance in list_instances:
            internals = []
            for internal in instance:
                internals.append(internal.__dict__)
            result.append(internals)
        return result

    def serialize(self):
        return {
            "entityId": self.__entityId,
            "mean_of_first_interval": self.__mean_of_first_interval,
            "mean_offset_from_first_symbol": self.__mean_offset_from_first_symbol,
            "mean_duration": self.__mean_duration,
            "mean_offset_from_start": self.__mean_offset_from_start,
            "mean_offset_from_end": self.__mean_offset_from_end,
            "symbolic_intervals": self.get_json_from_field(self.__symbolic_intervals),
        }

    def full_init(
        self,
        entityId,
        symbolic_intervals,
        mean_of_first_interval,
        mean_offset_from_first_symbol,
        mean_duration,
        mean_offset_from_start,
        mean_offset_from_end,
    ):
        self.__entityId: str = entityId
        self.__symbolic_intervals = symbolic_intervals
        self.__mean_of_first_interval = mean_of_first_interval
        self.__mean_offset_from_first_symbol = mean_offset_from_first_symbol
        self.__mean_duration: float = mean_duration
        self.__mean_offset_from_start: float = mean_offset_from_start
        self.__mean_offset_from_end: float = mean_offset_from_end
