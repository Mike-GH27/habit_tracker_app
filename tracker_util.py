"""
This module provides utility functions.

Functions:
    delete_file(file_name): deletes file with given name
    indate_typeconversion(indate): converts given date into datetime object
    get_date_string(indate): converts given datetime object into string with specified format
    days_difference(indate1, indate2): returns difference of days between dates
    day_streak(date1, date2): returns day difference + 1 between dates
    week_streak(date1, date2): returns week difference + 1 between dates
    is_long_year(inyear): checks if given year is an ISO long year
    filter_habit_list(inlist, period): returns list of habit objects with given periodicity
    filter_from_date(inlist, indate, mode): filters out dates before or after given date
    date_conversion(inlist): drops HH:MM:SS from datetime objects
    get_earliest_creation_date(inlist): returns earliest creation date from a list of habit objects
"""


import os
import calendar
from datetime import date, datetime


def delete_file(file_name) -> None:
    """Deletes file in current directory

    :param string file_name: name of the file to be deleted """
    if os.path.isfile(file_name):
        os.remove(file_name)


def indate_type_conversion(indate) -> datetime:
    """Converts string in %Y-%m-%d %H:%M:%S, date and datetime objects to datetime objects. Raises value error,
    if input does not match requirements

    :param indate: string in %Y-%m-%d %H:%M:%S, date or datetime objects
    :return: datetime"""
    if isinstance(indate, str):
        try:
            return datetime.strptime(indate, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError('String does not have correct %Y-%m-%d %H:%M:%S format')
    elif isinstance(indate, date):
        return datetime(indate.year, indate.month, indate.day)
    elif isinstance(indate, datetime):
        return indate
    else:
        raise TypeError("Input variable does not match expected data type")


def get_date_string(indate) -> str:
    """Returns datetime object as string in following format -> [September, 12, '23]

    :param datetime indate:
    :return: string"""
    month = indate.strftime("%B")
    year = indate.strftime("%y")
    return f"[{month}, {indate.day}, '{year}]"


def days_difference(indate1, indate2) -> int:
    """Calculates difference between two dates in days

    :param datetime indate1:
    :param datetime indate2:
    :return: integer"""
    # check which date is greater to avoid negative number
    # convert from datetime to date to avoid possible issues with hours, minutes and seconds
    date1 = date_conversion([indate1])[0]
    date2 = date_conversion([indate2])[0]
    if date2 > date1:
        return (date2 - date1).days
    else:
        return (date1 - date2).days


def day_streak(date1, date2) -> int:
    """Calculates streak of days between two dates. Order of days does not matter

    :param datetime date1:
    :param datetime date2:
    :return: integer"""
    if date1 is None or date2 is None:
        return 0
    return days_difference(date1, date2) + 1


def week_streak(indate1, indate2) -> int:
    """Calculates streak of weeks. Order of dates does not matter

    :param datetime indate1:
    :param datetime indate2:
    :return: int"""

    def compensate_for_long_years(year_start, year_end) -> int:
        """Returns number of weeks to be added in streak between >1 year
        :param int year_start:
        :param int year_end:
        :return: int: # of weeks
        """
        if year_end - year_start < 2:
            return 0
        if is_long_year(year_start + 1):
            temp_compensate = 1
        else:
            temp_compensate = 0
        return temp_compensate + compensate_for_long_years(year_start + 1, year_end)

    if indate1 is None or indate2 is None:
        return 0
    date1 = date_conversion([indate1])[0]
    date2 = date_conversion([indate2])[0]
    if date1 > date2:
        date_start = date2
        date_end = date1
    else:
        date_start = date1
        date_end = date2
    # case: same week -> streak of one
    if date_start.isocalendar()[1] == date_end.isocalendar()[1]:
        return 1
    # case: same year
    elif date_start.isocalendar()[0] == date_end.isocalendar()[0]:
        return date_end.isocalendar()[1] - date_start.isocalendar()[1] + 1
    # not same year
    else:
        year_start = date_start.isocalendar()[0]
        year_end = date_end.isocalendar()[0]
        week_compensation = compensate_for_long_years(year_start, year_end)

        if is_long_year(date_start.isocalendar()[0]):
            annual_weeks_start = 53
        else:
            annual_weeks_start = 52
        return ((annual_weeks_start - date_start.isocalendar()[1] + 1) + date_end.isocalendar()[1] +
                (date_end.isocalendar()[0] - date_start.isocalendar()[0] - 1)*52) + week_compensation


def is_long_year(inyear) -> bool:
    """Checks if year is a long year in ISO week date system.

    :param int inyear:
    :return: boolean """
    # checks if either the last day of the year or the first day of the next year is a Thursday
    # , which is the criteria for a ISO long year
    # 4 stands for Thursday
    # checks for leap year first as rules for long year differ from normal years to leap years
    if calendar.isleap(inyear):
        if datetime(inyear, 12, 31).isoweekday() == 5 or datetime(inyear, 1, 1).isoweekday() == 3:
            return True
        else:
            return False
    else:
        if datetime(inyear, 12, 31).isoweekday() == 4 or datetime(inyear, 1, 1).isoweekday() == 4:
            return True
        else:
            return False


def filter_habit_list(inlist, period) -> list:
    """Filters a list of habit object by period

    :param inlist: list of habit objects
    :type inlist: list
    :param period: [daily, weekly]
    :type period: string
    :return: list[habit] """
    def filter_period(x):
        return x.period == period

    return list(filter(filter_period, inlist))


def filter_from_date(inlist, indate, mode="before") -> list:
    """Filters out all dates before or after a given date


    :param inlist: list of datetime objects
    :type inlist: list
    :param indate: cutoff-date
    :type indate:datetime
    :param mode: [before, after]
    :type mode: string
    :return: list[datetime] """
    inlist_con = date_conversion(inlist)
    indate_con = date_conversion([indate])[0]

    if mode == "before":

        def check_date_before(indate2):
            if indate2 >= indate_con:
                return True
            else:
                return False

        return list(filter(check_date_before, inlist_con))

    elif mode == "after":

        def check_date_after(indate2):
            if indate2 <= indate_con:
                return True
            else:
                return False

        return list(filter(check_date_after, inlist_con))


def date_conversion(inlist):
    """Returns list of datetime object where hh:mm:ss are eliminated

    :param list[datetime] inlist: list of datetime objects
    :return: list of datetime objects"""
    if not inlist:
        return []

    def filter_date(invar):
        return datetime(invar.year, invar.month, invar.day)

    return list(map(filter_date, inlist))


def get_earliest_creation_date(inlist) -> datetime:
    """Returns earliest creation date from a list of habit objects. Returns datetime.min when input is empty list
    :param list[habit] inlist: list of habit objects
    """
    if not inlist:
        return datetime.min
    else:
        return sorted(inlist, key=lambda x: x.creation_date)[0].creation_date


if __name__ == '__main__':
    pass