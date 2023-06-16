"""
Functions for extracting household-level data from a general HETUS data set
"""

import logging
import time
import numpy as np
import pandas as pd

import hetus_columns as col


def group_rows_by_household(
    data: pd.DataFrame, select_mode: bool = False
) -> pd.DataFrame:
    """
    Extracts the household-level data from the data set. Produces a
    dataframe that uses year, country and HID as index.

    :param data: general HETUS data set
    :type data: pd.DataFrame
    :param select_mode: if True, uses the most frequent value for all
                        household level data, else the first value,
                        defaults to False
    :type select_mode: bool, optional
    :return: household-level data set
    :rtype: pd.DataFrame
    """
    start = time.time()
    # select household level columns and set country and HID as index
    grouped = data.groupby(col.HH.KEY)
    if select_mode:
        # select the most frequent value out of each group; this is better if there are different values per
        # group; this method is much slower than the one below
        grouped_data = grouped.agg(
            lambda x: (x.value_counts().index[0]) if len(x) > 0 else np.nan
        )
    else:
        # assume all values in the group are equal and simply select the first one
        grouped_data = grouped.first()
    logging.info(
        f"Extracted {len(grouped_data)} households from {len(data)} entries in {time.time() - start:.1f} s"
    )
    return grouped_data


def detect_household_level_columns(data: pd.DataFrame) -> pd.Index:
    """
    Analysis-function for checking which columns are actually on household
    level and thus always have the same value for all entries belonging to
    the same household.
    Can be used to check for which hosehold level columns the data
    is acutally consistent acrossall entries.

    :param data: hetus data
    :type data: pd.DataFrame
    :return: index containing all columns on household level
    :rtype: pd.Index
    """
    # count how many different values for each column there are within a single household
    num_values_per_hh = data.groupby(col.HH.KEY).nunique()
    # get the columns that always have the same value within a single household
    hh_data = (num_values_per_hh == 1).all(axis=0)  # type: ignore
    hh_data = hh_data.loc[hh_data == True]
    return hh_data.index


def extract_household_columns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Resets the index and removes all columns that are below household level, but
    keeps all rows (meaning there are multiple rows per household).

    :param data: general HETUS data set
    :type data: pd.DataFrame
    :return: data set containing only columns on household level
    :rtype: pd.DataFrame
    """
    assert (
        data.index.names == col.Diary.KEY
    ), "Invalid data: diary-level HETUS data required"
    # remove index and content columns below HH level (person and diary level)
    hhdata = data.reset_index().set_index(col.HH.KEY)[col.HH.CONTENT]
    return hhdata


def get_consistent_households(data: pd.DataFrame) -> pd.Index:
    """
    Returns households without inconsistent household-level data, e.g., where multiple
    diary entries for the same household specify different household sizes.

    :param data: DataFrame with inconsistent household data
    :type data: pd.DataFrame
    :return: Index containing only consistent households
    :rtype: pd.Index
    """
    assert (
        isinstance(data.index, pd.MultiIndex) and list(data.index.names) == col.HH.KEY
    ), f"Data has to have the following index: {col.HH.KEY}"
    # only keep columns on household level
    data = data[col.HH.CONTENT]
    # get numbers of different values per household for each column
    num_values_per_hh = data.groupby(level=col.HH.KEY).nunique()  # type: ignore
    inconsistent_columns_per_hh = (num_values_per_hh != 1).sum(axis=1)  # type: ignore
    # create an index that contains all consistent households
    consistent_households = inconsistent_columns_per_hh[
        inconsistent_columns_per_hh == 0
    ].index
    logging.info(
        f"Out of {len(num_values_per_hh)} households, {len(num_values_per_hh) - len(consistent_households)} are inconsistent."
    )
    return consistent_households


def get_complete_households(data: pd.DataFrame) -> pd.Index:
    """
    Returns a new dataframe, containing only complete households, meaning
    households where each inhabitant took part in the survey.

    :param data: general HETUS data set
    :type data: pd.DataFrame
    :return: complete households
    :rtype: pd.DataFrame
    """
    data = data.reset_index().set_index(col.HH.KEY)
    # group by household
    hhsizes = data[col.HH.SIZE].groupby(level=col.HH.KEY).first()  # type: ignore
    # get the number of survey participants per household
    participants_per_hh = data[col.Person.ID].groupby(level=col.HH.KEY).nunique()  # type: ignore
    merged = pd.concat([hhsizes, participants_per_hh], axis=1)
    # get households where the size matches the number of participants
    complete = merged[merged[col.Person.ID] == merged[col.HH.SIZE]].index
    logging.info(
        f"Out of {len(merged)} households, {len(merged) - len(complete)} are incomplete."
    )
    return complete


def filter_by_index(
    data: pd.DataFrame, index: pd.Index, keep_entries: bool = True
) -> pd.DataFrame:
    """
    Filters a data set using a separate index. The keep_entries parameter determines which part of
    the data is kept.

    :param data: the data to filter
    :type data: pd.DataFrame
    :param index: the index used as filter condition
    :type index: pd.Index
    :param keep_entries: True if the entries in index should be kept, else false; defaults to True
    :type keep_entries: bool, optional
    :return: the filtered data set
    :rtype: pd.DataFrame
    """
    inindex = data.index.isin(index)
    keep = inindex if keep_entries else ~inindex
    return data.loc[keep]


def get_usable_household_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the data on household-level from the specified data set.
    Removes entries with incomplete or inconsistent data.

    :param data: general HETUS data set
    :type data: pd.DataFrame
    :return: data set on households
    :rtype: pd.DataFrame
    """
    data = filter_by_index(data, get_complete_households(data))
    data = extract_household_columns(data)
    data = filter_by_index(data, get_consistent_households(data))
    hhdata = group_rows_by_household(data, False)
    return hhdata
