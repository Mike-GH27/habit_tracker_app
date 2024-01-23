"""
This module provides functions to analyze habit completion data

count_habit(inlist, period): counts number of completions for given period and list of habits
habit_completion_counts(inlist, indate_early, indate_late): counts number of completion for each habit in giuven period
completions_habits(inlist, indate_early, indate_late): returns stats like actual and potential completions
habit_completion_stats(inlist, indate_early, indate_end): returns table with habit data and completion statistics
performance(df, mode): returns best or worst performing habits or ranking
streaks_longest(input_list, period): returns longest streaks for given completion dates
streak_current(inlist, period, indate): returns current streak for given completion dates
habit_streak_stats(inlist): returns habit information and streak statistics for given list of habits
streak_data(df, mode): returns streak stats and habit info for longest current or all_time streaks
completion_dates_statistics(habit): returns completion dates grouped by year and month
count_completion_dates_statistics(habit): counts completions per month in each year
"""

import pandas as pd
import tracker
import tracker_util
from datetime import datetime, timedelta
from functools import reduce


def count_habit(inlist=tracker.Habit.habit_list, period="all") -> int:
    """Counts number of times habits have been completed

    :param list[habit] inlist:
    :param string period: [daily, weekly, all]
    :return: integer"""
    if period == "daily":
        period_list = tracker_util.filter_habit_list(inlist, period)
    elif period == "weekly":
        period_list = tracker_util.filter_habit_list(inlist, period)
    else:
        period_list = inlist

    def map_number_of_completions(habit):
        return len(habit.complete_time_list)

    return reduce(lambda x, y: x + y, list(map(map_number_of_completions, period_list)))


def habit_completion_counts(inlist, indate_early, indate_late=datetime.today()) -> list:
    """Calculates number of completions for each habit for a list of habit objects

    :param list[habit] inlist: list of habit objects
    :param datetime indate_early: cutoffdate early
    :param datetime indate_late: cutoffdate later
    :return: list[int]: list of integers
    """
    # change period end points of weekly habits to include entire week
    def map_week_period_date_early(x) -> datetime:
        """Changes period start date to beginning of the calendar week
        :param habit object x: habit object
        :returns: datetime: period start"""
        if x.period == "daily":
            return indate_con_early
        elif x.period == "weekly":
            return indate_con_early - timedelta(days=(indate_con_early.isoweekday() - 1))

    def map_week_period_date_late(x) -> datetime:
        """Changes period end date to end of the calendar week
        :param habit object x: habit object
        :returns: datetime: period end"""
        if x.period == "daily":
            return indate_con_late
        elif x.period == "weekly":
            return indate_con_late + timedelta(days=(7 - indate_con_late.isoweekday()))

    # empty input
    if not inlist:
        return []
    # dropping HH:MM:SS
    indate_con_early = tracker_util.date_conversion([indate_early])[0]
    indate_con_late = tracker_util.date_conversion([indate_late])[0]
    # auxiliary lists for map operations
    aux_list_mode_early = ["before"] * (count_habit(inlist) + len(inlist))
    aux_list_mode_late = ["after"] * (count_habit(inlist) + len(inlist))

    # adapt period dates so that they capture entire calendar week
    aux_list_indate_early_adapted = list(map(map_week_period_date_early, inlist))
    aux_list_indate_late_adapted = list(map(map_week_period_date_late, inlist))

    # list of complete_time_list attributes of habit objects
    list_completion_date_lists = list(map(lambda x: x.complete_time_list, inlist))

    # filter out all dates prior to indate_early
    list_completion_date_lists_filtered_before = list(map(tracker_util.filter_from_date,
                                                          list_completion_date_lists,
                                                          aux_list_indate_early_adapted,
                                                          aux_list_mode_early))
    # filter out all dates after indate_late
    list_completion_date_lists_filtered_after = list(map(tracker_util.filter_from_date,
                                                         list_completion_date_lists_filtered_before,
                                                         aux_list_indate_late_adapted,
                                                         aux_list_mode_late))
    # calculate number of completions for each habit
    return list(map(lambda x: len(x), list_completion_date_lists_filtered_after))


def completions_habits(inlist, indate_start=datetime(1900, 1, 1), indate_end=datetime.today()) -> tuple:
    """Returns lists of actual completions, potential completions and relationship between period and creation date
     in a given period. List indices of output list correspond to list indices of input list. Order of start and end
     date do not matter

    :param list inlist: list of habits
    :param datetime indate_start: period start
    :param datetime indate_end: period end
    :return: list[int], list[int], list[int], list[int], list[int]: see list indices

    ----

    list indices:

    0=actual completion counts

    1=potential completion since period start

    2=period to creation date relationship code

    3=potential completions since creation date

    4=completion in period with regard to creation date

    5=completion percentage in period (based on max(period start, creation_date)

    ----

    period to creation date relationship code:

    0=end date is before creation date

    1=start is before creation date

    2=start date is creation date

    3=start date is after period start

    ----

    """
    # drop HH:MM:SS
    indate_start_c_temp = tracker_util.date_conversion([indate_start])[0]
    indate_end_c_temp = tracker_util.date_conversion([indate_end])[0]
    # correcting start and end dates of period
    if indate_start_c_temp > indate_end_c_temp:
        indate_start_c = indate_end_c_temp
        indate_end_c = indate_start_c_temp
    else:
        indate_start_c = indate_start_c_temp
        indate_end_c = indate_end_c_temp

    def map_potential_completions_since_period_start(x) -> int:
        """Returns potential completions of a habit in given period

        :param x: habit object"""
        start_date2 = max(x.creation_date, indate_start_c)
        if x.period == "daily":
            if start_date2 > indate_end_c:
                return 0
            else:
                return tracker_util.day_streak(start_date2, indate_end_c)
        elif x.period == "weekly":
            # check if start date is after end date in terms of calendar week
            if (start_date2 - timedelta(days=start_date2.isoweekday() - 1) >
                    (indate_end_c - timedelta(days=indate_end_c.isoweekday() - 1))):
                return 0
            else:
                return tracker_util.week_streak(start_date2, indate_end_c)

    def map_creation_date_code(x) -> int:
        """Returns position of period in relation to start date

        [0=end date is before creation date,
        1=start is before creation date,
        2=start date is creation date,
        3=start date is after creation date]

        :param x: habit object"""
        creation_date = tracker_util.date_conversion([x.creation_date])[0]
        if indate_end_c < creation_date:
            return 0
        elif indate_start_c < creation_date:
            return 1
        elif indate_start_c == creation_date:
            return 2
        elif indate_start_c > creation_date:
            return 3

    def map_potential_completions_since_creation_date(x) -> int:
        """Returns potential completions of a habit since creation date

        :param x: habit object
        :return: int: potential completions"""
        start_date2 = tracker_util.date_conversion([x.creation_date])[0]
        if start_date2 > indate_end_c:
            return 0
        if x.period == "daily":
            if start_date2 > indate_end_c:
                return 0
            else:
                return tracker_util.day_streak(start_date2, indate_end_c)
        elif x.period == "weekly":
            # check if start date is after end date in terms of calendar week
            if (start_date2 - timedelta(days=start_date2.isoweekday() - 1) >
                    (indate_end_c - timedelta(days=indate_end_c.isoweekday() - 1))):
                return 0
            else:
                return tracker_util.week_streak(start_date2, indate_end_c)

    def map_completion_percentage(completion, potential_completion) -> int | None:
        """Returns completion percentage in given period. Note: if creation date is later than period start then
        it will be computed until creation date
        :param int completion: # of habit completion in period
        :param int potential_completion: potential completions since what is later: period start or creation date
        :return: int: completion percentage
        """
        if potential_completion == 0:
            return None
        return int(completion / potential_completion * 100)

    def map_potential_completions_period_creation_date(pot_comp_per, pot_comp_cre, code) -> int:
        """Returns potential completions since what is later: period start or creation date

        :param int pot_comp_per: # of potential completions of habit in period
        :param int pot_comp_cre: # of potential completion of habit from period start to creation date
        :param int code: code for relationship between creation date and period -> see outer function for explanation
        :return: int: potential completions"""
        if code == 3:
            completion_count = pot_comp_per
        else:
            completion_count = pot_comp_cre
        return completion_count

    out_completion_counts = habit_completion_counts(inlist, indate_start, indate_end)
    out_potential_completions_period_start = list(map(map_potential_completions_since_period_start, inlist))
    out_potential_completions_creation_date = list(map(map_potential_completions_since_creation_date, inlist))
    out_date_rel_codes = list(map(map_creation_date_code, inlist))
    out_potential_completions_period_creation_date = list(map(map_potential_completions_period_creation_date,
                                                              out_potential_completions_period_start,
                                                              out_potential_completions_creation_date,
                                                              out_date_rel_codes))
    out_completion_percentage = list(map(map_completion_percentage,
                                         out_completion_counts,
                                         out_potential_completions_period_creation_date))

    return (out_completion_counts,
            out_potential_completions_period_start,
            out_date_rel_codes,
            out_potential_completions_creation_date,
            out_potential_completions_period_creation_date,
            out_completion_percentage)


def habit_completion_stats(inlist, indate_start=datetime(1900, 1, 1), indate_end=datetime.today()) \
        -> pd.DataFrame:
    """Returns pandas dataframe with habit attributes and statistics on performance in given period

    :param list[habit] inlist: list of habit objects
    :param datetime indate_start: start of period
    :param datetime indate_end: end of period
    :return: list of tuples

    x-axis indices: habit IDs

    y-columns:

    description[dtype] - column name

    0. habit object[habit object] - object

    1. habit name[str] - name

    2. habit period[str] - period

    3. creation_date[datetime] - credate

    4. actual completion counts[int] - act_complet

    5. potential completion since period start[int] - pot_complet_per

    6. period to creation date relationship code[int] - per_credate_code
        [0=end date is before creation date,
        1=start is before creation date,
        2=start date is creation date,
        3=start date is after creation date]

    7. potential completions since creation date[int] - pot_complet_credate

    8. potential completion in period with regard to creation date[int] - pot_complet_per_credate

    9. completion percentage in period (based on max(period start, creation_date)[int] - complet_percent

    """
    if not inlist:
        return pd.DataFrame()

    habit_ids = list(map(lambda x: x.habit_id, inlist))
    habit_names = list(map(lambda x: x.habit_name, inlist))
    habit_period = list(map(lambda x: x.period, inlist))
    habit_credate = list(map(lambda x: x.creation_date, inlist))

    statistics = completions_habits(inlist, indate_start, indate_end)

    df = pd.DataFrame({
        "object": inlist,
        "id": habit_ids,
        "name": habit_names,
        "period": habit_period,
        "credate": habit_credate,
        "act_complet": statistics[0],
        "pot_complet_per": statistics[1],
        "per_credate_code": statistics[2],
        "pot_complet_credate": statistics[3],
        "pot_complet_per_credate": statistics[4],
        "complet_percent": statistics[5]
    })

    return df.set_index('id')


def performance(df, mode) -> pd.DataFrame:
    """Returns "best" or "worst" performing habits or gives "overview" by sorting habits
    by performance[best first by completion % and then # of completions]
    :param pandas.dataframe df: data on performance and habits
    :param string mode: [best, worst, overview]
    :return: pandas.Dataframe
    """
    if mode == "best":
        return df[df['complet_percent'] == df['complet_percent'].dropna().max()]
    elif mode == "worst":
        return df[df['complet_percent'] == df['complet_percent'].dropna().min()]
    elif mode == "overview":
        return df.sort_values(['complet_percent', 'act_complet'], ascending=False)


def streaks_longest(input_list, period) -> tuple:
    """Returns duration of longest streak and list of longest streak start and end dates for a list of dates

    :param list[datetime] input_list: list of completion dates
    :param str period: [daily, weekly]
    :return: tuple[int, list[tuple[datetime, datetime]]:
    longest streak, list of [start date, end dates] of longest streaks"""
    if not input_list:
        return 0, []
    if period == "daily":
        streak_func = tracker_util.day_streak
    else:  # period == "weekly":
        streak_func = tracker_util.week_streak

    def rec_streak_longest(inlist):
        """Returns longest streak start and end date in sliced list (start represents list index)
        :param list[datetime] inlist: list of completion dates
        :return: list[tuple[datetime, datetime]]: streak start and end dates"""
        # empty list, no streak
        if not inlist:
            return []
        # one element means only one one-day streak
        elif len(inlist) == 1:
            return [(inlist[0], inlist[0])]
        # >1 elements
        else:
            # extension of current streak
            temp_list = rec_streak_longest(inlist[1:])
            # possible streak that get extended is last element in list
            # 2 day streak means streak extension
            if streak_func(temp_list[-1][0], inlist[0]) == 2:
                out_tuple = (inlist[0], temp_list[-1][1])
                # check if current streak is larger than previous longest streak
                if (streak_func(out_tuple[0], out_tuple[1]) >
                        streak_func(temp_list[0][0], temp_list[0][1])):
                    # if larger return current streak as longest streak
                    return [out_tuple]
                else:
                    # if not larger "extend" list by current streak
                    out_list = temp_list + [out_tuple]
                    return out_list
            # > 1 day difference extension means new streak
            else:
                out_tuple = (inlist[0], inlist[0])
                return temp_list + [out_tuple]

    def filter_streak(intuple) -> bool:
        """
        Filters out streaks =/= longest streak

        :param tuple[datetime, datetime] intuple: streak start and end date
        :return: boolean
        """
        return streak_func(intuple[0], intuple[1]) == streak_length

    streak_list = rec_streak_longest(input_list)
    streak_length = streak_func(streak_list[0][0], streak_list[0][1])
    return streak_length, list(filter(filter_streak, streak_list))


def streak_current(inlist, period, indate=datetime.today()):
    """Returns duration of longest current streak and start date

        :param list[datetime] inlist: list of completion dates
        :param str period: [daily, weekly]
        :param datetime indate: date which should be considered current date
        :return: tuple[int, datetime]:
        current streak, start date of current streak"""
    if not inlist:
        return 0, None

    if period == "daily":
        streak_func = tracker_util.day_streak
    elif period == "weekly":
        streak_func = tracker_util.week_streak
    # gap between current date and latest completion date
    if streak_func(inlist[-1], indate) > 2:
        return 0, None

    def current_streak(inlist):
        """Returns start date of current streak if inlist has >1 elements
        :param list[datetome] inlist: completion dates
        :return: datetime: start date of current streak
        """
        if len(inlist) == 1:
            return inlist[0]
        elif streak_func(inlist[-2], inlist[-1]) > 2:
            return inlist[-1]
        else:
            return current_streak(inlist[:-1])

    out_streak = current_streak(inlist)

    return streak_func(out_streak, inlist[-1]), out_streak


def habit_streak_stats(inlist) -> pd.DataFrame:
    """Returns a pandas.Dataframe with object attributes and streak statistics

    :param list[habit] inlist: list of habit objects
    :return: pandas Dataframe

    x-axis indices: habit IDs

    y-columns:

    description[dtype] - column name

    0. habit object[habit object] - object

    1. habit name[str] - name

    2. habit period[str] - period

    3. creation_date[datetime] - credate

    4. current streak length[int] - streak_c_length

    5. start date of current streak[datetime] - streak_c_date

    6. longest streak length[int] -  streak_l_length

    7. start and end dates of longest streaks[list[tuple[datetime]] - streak_l_dates

    """
    if not inlist:
        return pd.DataFrame()

    habit_ids = list(map(lambda x: x.habit_id, inlist))
    habit_names = list(map(lambda x: x.habit_name, inlist))
    habit_period = list(map(lambda x: x.period, inlist))
    habit_credate = list(map(lambda x: x.creation_date, inlist))
    habit_comptimes = list(map(lambda x: x.complete_time_list, inlist))

    current_streak = list(map(streak_current, habit_comptimes, habit_period))
    longest_streak = list(map(streaks_longest, habit_comptimes, habit_period))
    list_streak_current_length = list(map(lambda x: x[0], current_streak))
    list_streak_current_date = list(map(lambda x: x[1], current_streak))
    list_streak_longest_length = list(map(lambda x: x[0], longest_streak))
    list_streak_longest_dates = list(map(lambda x: x[1], longest_streak))

    df = pd.DataFrame({
        "object": inlist,
        "id": habit_ids,
        "name": habit_names,
        "period": habit_period,
        "credate": habit_credate,
        "streak_c_length": list_streak_current_length,
        "streak_c_date": list_streak_current_date,
        "streak_l_length": list_streak_longest_length,
        "streak_l_dates": list_streak_longest_dates
    })

    return df.set_index("id")


def streak_data(df, mode):
    """Returns pandas.Dataframe with habits having the longest [daily, longest] streaks
    :param pandas.Dataframe df: streak statistics
    :param mode: [current, longest]
    :return: pandas.Dataframa: habits with longest [current, longest] streaks

    x-axis indices: habit IDs

    y-columns:

    description[dtype] - column name

    0. habit object[habit object] - object

    1. habit name[str] - name

    2. habit period[str] - period

    3. creation_date[datetime] - credate

    4. current streak length[int] - streak_c_length

    5. start date of current streak[datetime] - streak_c_date

    6. longest streak length[int] -  streak_l_length

    7. start and end dates of longest streaks[list[tuple[datetime]] - streak_l_dates

    """
    if df.empty:
        return df
    if mode == "current":
        return df[df['streak_c_length'] == df['streak_c_length'].max()]
    elif mode == "longest":
        return df[df['streak_l_length'] == df['streak_l_length'].max()]


def completion_dates_statistics(habit) -> tuple:
    """Returns completion dates per year and month
    :param habit habit: habit-object
    :return: tuple[tuple[tuple[datetime]]]: completion dates per month
    indexes:
    [] = year
    [][] = month
    [][][] = datetime
    """
    inlist = habit.complete_time_list
    if not inlist:
        return ()
    list_years = list(range(datetime.today().year, habit.creation_date.year - 1, -1))

    def year_filter(year, dates):
        """Filters out all dates unequal to given year
        :param year: wanted year
        :param dates:
        :return: list[bool]: True -> year of date matches input year
        """
        return list(filter(lambda x: x.year == year, dates))

    list_dates_by_year = list(map(year_filter, list_years, [inlist]*len(list_years)))

    def year_month_filter(dates_by_year):
        """
        :param dates_by_year: list of dates in a year
        :return: tuple[tuple[datetime]]: tuple with tuples of datetime objects for each month
        """
        dates_by_year_list = [dates_by_year]*12
        months = list(range(1, 13))

        def month_filter(dates, inmonth) -> tuple:
            """filters out all dates which are not in inmonth

            :param list[datetime] dates: list of dates in a year
            :param int inmonth: month number
            :return: tuple[datetime]: tuple of datetime objects in month
            """
            return tuple(filter(lambda x: x.month == inmonth, dates))

        return tuple(map(month_filter, dates_by_year_list, months))

    list_dates_by_year_month = tuple(map(year_month_filter, list_dates_by_year))

    return list_dates_by_year_month


def count_completion_dates_statistics(habit) -> tuple:
    """Counts completion dates of habit per month and year
    :param habit habit: habit-object
    :return: tuple[tuple[int]]: completion counts by month in each year. Index 0 is the most recent year
    indexes:
    [] = year -> 0 = most recent year
    [][] = month -> indexes are in order of calendar 0 -> January
    """
    inlist = habit.complete_time_list
    if not inlist:
        return ()

    intuple = completion_dates_statistics(habit)

    def sum_months(intuple) -> tuple:
        """Counts all values in each tuple
        :param tuple[tuple[datetime]] intuple: completion dates per month
        :return: tuple[int]: completions per month
        """
        return tuple(map(lambda x: len(x), intuple))

    return tuple(map(sum_months, intuple))


if __name__ == '__main__':
    pass
