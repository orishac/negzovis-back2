from abc import ABC, abstractmethod
from math import inf

import pandas as pd
import portion as interval

from constants import DatasetColumns, StatesColumns
from utils.dataframes_generator import DataframesGenerator


class TemporalAbstraction(ABC):

    @staticmethod
    @abstractmethod
    def discretize_property(prop_df):
        """ this is an abstract method """

    @staticmethod
    def discretize_to_bins(cutpoints, values):
        """
        making the values given as parameter discrete according to the cutpoints given
        :param cutpoints: List, a list of cutpoints to discretize by
        :param values: List, a list of values to discretize
        :return: List, a list of discrete values
        """

        # added -inf and +inf at each edge to ignore calculation errors and to keep only the relevant ranges for the user
        bins = [-inf] + sorted(cutpoints) + [inf]  # added sorted() method to fix monotonically increase of bins
        discrete_values = pd.cut(values, bins=bins, labels=False)
        return discrete_values

    @staticmethod
    def create_symbolic_time_series(states, time_point_series):
        """
        Creates a symbolic time series from a given states dataframe and a time point series
        :param states: Dataframe, a states dataframe
        :param time_point_series: Dataframe, a time point series
        :return:
            Dataframe, a symbolic time series so that each TemporalPropertyValue was replaced with
            its corresponding StateID
        """
        if states.empty or time_point_series.empty:
            return DataframesGenerator.generate_empty_symbolic_time_series()

        dataset_df = time_point_series.copy()

        cutpoints = TemporalAbstraction.extract_cutpoints_from_states(states)

        for prop_id, cutoffs in cutpoints.items():
            df_prop_idx = (dataset_df.TemporalPropertyID == prop_id)
            dataset_df.loc[df_prop_idx, StatesColumns.BinID] = \
                TemporalAbstraction.discretize_to_bins(cutpoints[prop_id],
                                                       dataset_df[df_prop_idx].TemporalPropertyValue)

        symbolic_time_series = dataset_df.drop(DatasetColumns.TemporalPropertyValue, axis='columns')

        symbolic_time_series = symbolic_time_series.join(
            states[[StatesColumns.StateID,
                    StatesColumns.TemporalPropertyID,
                    StatesColumns.BinID]].set_index([StatesColumns.TemporalPropertyID, StatesColumns.BinID]),
            how='left',
            on=[StatesColumns.TemporalPropertyID, StatesColumns.BinID]
        )

        return symbolic_time_series.drop(StatesColumns.BinID, axis='columns')

    @staticmethod
    def extract_cutpoints_from_states(states):
        """
        Extracts a list of cutpoints from the states dataframe for each property
        :param states: Dataframe, a dataframe containing states
        :return: Dict, a dictionary mapping each property-id to its list of cutpoints
        """
        cutpoints = {}

        for prop_id, prop_df in states.groupby(by=DatasetColumns.TemporalPropertyID):
            if len(prop_df) == 1:
                try:  # avoids errors caused by string values of negative numbers
                    bin_low = prop_df.BinLow.astype(float).item()
                    bin_high = prop_df.BinHigh.astype(float).item()
                    if bin_low != -inf and bin_high != inf:
                        cutpoints[prop_id] = [bin_low, bin_high]
                    elif bin_low != -inf:
                        cutpoints[prop_id] = [bin_low]
                    elif bin_high != inf:
                        cutpoints[prop_id] = [bin_high]
                    else:  # bin_low == -inf and bin_high == inf:
                        cutpoints[prop_id] = []
                except ValueError:
                    cutpoints[prop_id] = [prop_df.BinHigh.astype(float).item()]
            else:  # extracts all BinHigh values except the last one. It will fill the final edge in discretize_to_bins
                cutpoints[prop_id] = list(prop_df.BinHigh[:-1].astype(float))

        return cutpoints

    @staticmethod
    def is_valid_states(states, allow_non_continuous_range):
        is_valid = True
        is_valid &= states[StatesColumns.StateID].is_unique
        for name, group in states.groupby(by=DatasetColumns.TemporalPropertyID):
            is_valid &= group[StatesColumns.BinID].is_unique
            for index, row in group.iterrows():
                if index < len(group.index) - 1:
                    non_overlaps = (interval.open(group['BinLow'][index], group['BinHigh'][index]) & interval.open(
                        group['BinLow'][index + 1], group['BinHigh'][index + 1])).empty
                    is_valid &= non_overlaps
                    if not is_valid:
                        break
                    if allow_non_continuous_range:
                        continue
                    continuous_range = not (
                            interval.closed(group['BinLow'][index], group['BinHigh'][index]) & interval.closed(
                        group['BinLow'][index + 1], group['BinHigh'][index + 1])).empty
                    is_valid &= continuous_range
                    if not is_valid:
                        break

        return is_valid
