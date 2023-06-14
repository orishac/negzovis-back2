from functools import reduce

from constants import StatesColumns, DatasetColumns, MethodsNames
from temporal_abstraction.temporal_abstraction import TemporalAbstraction
from utils.dataframes_generator import DataframesGenerator


class KnowledgeBased(TemporalAbstraction):
    """
        Handles knowledge-based temporal abstraction
    """

    def __init__(self, states, ncr=False):
        if states is not None:
            if not TemporalAbstraction.is_valid_states(states, ncr):
                raise Exception('ERROR: States input is invalid')
            if StatesColumns.Method in states.columns:
                curr_states = states[states[StatesColumns.Method] == MethodsNames.KnowledgeBased]
                l_titles = list(curr_states.columns)
                l_titles.insert(len(l_titles) - 1, l_titles.pop(l_titles.index(StatesColumns.Method)))
                curr_states = curr_states.loc[:, l_titles]
                self.__states = curr_states
            else:
                states[StatesColumns.Method] = MethodsNames.KnowledgeBased
                self.__states = states

    @staticmethod
    def knowledge_based(states, prop_df):
        """
        :param states: Dataframe
        :param prop_df: Dataframe
        :return:
        """
        if StatesColumns.Method in states.columns:
            states = states[states[StatesColumns.Method] == MethodsNames.KnowledgeBased]
            symbolic_time_series = TemporalAbstraction.create_symbolic_time_series(states, prop_df)
            symbolic_time_series[StatesColumns.Method] = MethodsNames.KnowledgeBased
            return symbolic_time_series
        else:
            return TemporalAbstraction.create_symbolic_time_series(states, prop_df)

    def discretize_property(self, prop_df):
        if prop_df.empty:
            return DataframesGenerator.generate_empty_states(), DataframesGenerator.generate_empty_symbolic_time_series()
        prop_id = prop_df[DatasetColumns.TemporalPropertyID].values[0]
        return self.__states[self.__states[StatesColumns.TemporalPropertyID] == prop_id], \
               KnowledgeBased.knowledge_based(self.__states, prop_df)
