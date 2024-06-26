"""
Contains column names of HETUS data, ordered by level.

Remark: due to inconsistencies in the data, all column headers are
converted to upper case after parsing.
"""

import abc

import pandas as pd


class HetusLevel(abc.ABC):
    """
    Abstract base class for defining a HETUS level. A level
    is a layer in the data with a specific granularity.
    Multiple items of a certain level are contained in each
    item of the next higher level.
    On the highest level is the year, which is the same for
    the whole HETUS 2010 data set. Below is the country, then
    household, person and diary.
    Data in the HETUS SUF files is not normalized, so each row
    contains the full set of columns, which results in lots of
    redundant (and in part contradictory) information. The
    level structure here helps to work with this data
    structure.
    """

    NAME = ""
    ID = ""
    KEY: list[str] = []
    CONTENT: list[str] = []


class Year(HetusLevel):
    """
    Column names on year level
    """

    NAME = "Year"
    ID = "YEAR"
    KEY = [ID]


class Country(HetusLevel):
    """
    Column names on country level
    """

    NAME = "Country"
    ID = "COUNTRY"
    KEY = Year.KEY + [ID]


class HH(HetusLevel):
    """
    Column names on household level.
    This encompasses all columns that describe features of the
    household rather than of a person or a sinlge diary entry,
    and that should therefore be the same for all entries
    belonging to the same household (which is not the case in
    the actual data).
    """

    NAME = "Household"

    #: ID of the household
    ID = "HID"
    #: unique key for a household: COUNTRY + HID
    KEY = Country.KEY + [ID]

    #: number of persons in the household
    SIZE = "HHC1"
    HOUSE_TYPE = "HHQ3_1"
    NUM_CARS = "HHQ6P"

    #: all columns on household level besides the key columns
    CONTENT = [
        SIZE,
        "HHC3",
        "HHC4",
        "HHC5",
        HOUSE_TYPE,
        "HHQ4",
        "HHQ5",
        "HHQ6C",
        "HHQ6D",
        "HHQ6E",
        "HHQ6F",
        "HHQ6G",
        "HHQ6H",
        "HHQ6K",
        "HHQ6L_1",
        "HHQ6M",
        "HHQ6N",
        "HHQ6O",
        "HHQ6R",
        NUM_CARS,
        "HHQ9_1",
        "HHQ10A",
        "HHQ10F",
    ]
    #: all columns on household level
    ALL = KEY + CONTENT


class Person(HetusLevel):
    """
    Column names on personal level.
    This encompasses all columns with information on the respondent,
    e.g., sex or age.
    """

    NAME = "Person"
    ID = "PID"
    KEY = HH.KEY + [ID]

    SEX = "INC1"
    AGE_GROUP = "INC2"
    LIFECYCLE = "INC3"
    WORK_STATUS = "INC4_1"
    WORK_LAST_WEEK = "IND1"
    WYH_NOT_WORK_LAST_WEEK = "IND2"
    EMPLOYMENT_STATUS = "IND6_1"
    CONTRACT_TYPE = "IND44"
    FULL_OR_PART_TIME = "IND7"
    MULTIPLE_JOBS = "IND14"
    WEEKLY_WORKING_HOURS = "IND38"
    SELF_DECL_LABOUR_STATUS = "IND17_1"
    PERSON_WEIGHT = "WGHT2"

    CONTENT = [
        SEX,
        AGE_GROUP,
        LIFECYCLE,
        WORK_STATUS,
        WORK_LAST_WEEK,
        EMPLOYMENT_STATUS,
        CONTRACT_TYPE,
        FULL_OR_PART_TIME,
        MULTIPLE_JOBS,
        WEEKLY_WORKING_HOURS,
        SELF_DECL_LABOUR_STATUS,
        PERSON_WEIGHT,
    ]
    #: all columns on person level
    ALL = KEY + CONTENT


class Diary(HetusLevel):
    """
    Column names on the diary level (mostly date info)
    """

    NAME = "Diary"
    ID = "DIARY"
    KEY = Person.KEY + [ID]

    WEEKDAY = "DDV1"
    MONTH = "DDV3"
    YEAR = "DDV4"
    EMPLOYED_STUDENT = "DDV6"
    DAYTYPE = "DDV7"

    DAY_AND_PERSON_WEIGHT = "WGHT1"

    MAIN_ACTIVITIES_PATTERN = "MACT"
    MAIN_ACTIVITIES_AGG_PATTERN = "PACT"


def get_activity_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns only the activity data columns (MACT1 - MACT144).
    Returns a view on the original dataframe.

    :param data: HETUS diary data
    :return: view on only the activity data
    """
    return data.filter(like=Diary.MAIN_ACTIVITIES_PATTERN)
