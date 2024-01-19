import unittest
import sys
import os

import pandas as pd

import tracker_testing_data
from pandas import isnull
from datetime import datetime, timedelta

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import analytics_module
import tracker
import tracker_util


class Test_Count_Habit(unittest.TestCase):

    def setUp(self):
        tracker_testing_data.load_test_data()

    def tearDown(self):
        tracker.Habit.habit_list.clear()

    def test_count_habit_all_periods(self):
        self.assertEqual(41, analytics_module.count_habit(), "Does not count number of habit completions "
                                                             "for all periods properly")

    def test_count_habit_daily_periods(self):
        self.assertEqual(27, analytics_module.count_habit(period="daily"),
                         "Does not count number of habit completions for daily periods properly")

    def test_count_habit_weekly_periods(self):
        self.assertEqual(14, analytics_module.count_habit(period="weekly"),
                         "Does not count number of habit completions for weekly periods properly")


class Test_Habit_Completion_Counts(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        self.habit_list.clear()
        self.h1 = tracker.Habit("h1", "daily")
        self.h2 = tracker.Habit("h2", "daily")
        self.h3 = tracker.Habit("h3", "weekly")
        self.h4 = tracker.Habit("h4", "weekly")
        self.new_date_1 = datetime(2023, 12, 20)
        self.new_date_2 = datetime(2023, 12, 19)
        self.new_date_3 = datetime(2023, 12, 18)
        self.new_date_4 = datetime(2023, 12, 17)
        self.new_date_5 = datetime(2023, 12, 16)
        self.new_date_6 = datetime(2023, 12, 13)
        self.new_date_7 = datetime(2023, 12, 6)
        self.new_date_8 = datetime(2023, 12, 1)
        self.new_date_9 = datetime(2023, 11, 26)
        self.new_date_10 = datetime(2023, 11, 22)
        self.new_date_11 = datetime(2023, 11, 13)
        self.new_date_12 = datetime(2023, 11, 12)
        self.h1.complete_time_list.extend(
            [self.new_date_12, self.new_date_10, self.new_date_7, self.new_date_4, self.new_date_1])
        self.h2.complete_time_list.extend(
            [self.new_date_11, self.new_date_9, self.new_date_8, self.new_date_6, self.new_date_5])
        self.h3.complete_time_list.extend(
            [self.new_date_12, self.new_date_11, self.new_date_6, self.new_date_1])
        self.h4.complete_time_list.extend(
            [self.new_date_9, self.new_date_4, self.new_date_3])

    def tearDown(self):
        self.habit_list.clear()

    def test_completion_counts_empty_input_list(self):
        self.test_list = []
        self.assertEqual([], analytics_module.habit_completion_counts(self.test_list, datetime.today()),
                         "Completion count does not work properly if input list is empty")

    def test_completion_counts_no_completed_dates(self):
        test_habit = tracker.Habit("jogging", "daily")
        self.assertEqual([0], analytics_module.habit_completion_counts([test_habit], datetime.today()),
                         "Completion count does not work properly "
                         "if all complete_time_lists are empty (i.e. no habit has been completed")

    def test_completion_counts_case_today(self):
        self.test_date = self.new_date_1
        self.assertEqual([1, 0, 1, 1], analytics_module.habit_completion_counts(self.habit_list, self.test_date),
                         "Habit completion count does not work properly if cut-off date is today")

    def test_completion_counts_case_20_day_from_today_not_element(self):
        self.test_date = datetime(2023, 11, 30)
        self.assertEqual([3, 3, 2, 2], analytics_module.habit_completion_counts(self.habit_list, self.test_date),
                         "Habit completion count does not work properly "
                         "if cut-off dates are not element of input lists")

    def test_completion_counts_case_24_day_from_today_is_element(self):
        self.test_date = datetime(2023, 11, 26)
        self.assertEqual([3, 4, 2, 3], analytics_module.habit_completion_counts(self.habit_list, self.test_date),
                         "Habit completion count does not work properly "
                         "if cut-off dates are elements of input lists")

    def test_completion_counts_case_20_day_not_element(self):
        self.test_date = datetime(2023, 11, 30)
        self.test_date2 = datetime(2023, 12, 15)
        self.assertEqual([1, 2, 1, 1], analytics_module.habit_completion_counts(self.habit_list,
                                                                                self.test_date, self.test_date2),
                         "Habit completion count does not work properly "
                         "if cut-off date are not elements of input lists")

    def test_completion_counts_case_28_day_is_element(self):
        self.test_date = datetime(2023, 11, 26)
        self.test_date2 = datetime(2023, 12, 18)
        self.assertEqual([2, 4, 2, 3], analytics_module.habit_completion_counts(self.habit_list,
                                                                                self.test_date, self.test_date2),
                         "Habit completion count does not work properly "
                         "if cut-off date are elements of input lists")

    def test_completion_count_weekly_start_date_mid_week(self):
        self.h5 = tracker.Habit("h5", "weekly")
        self.new_date_13 = datetime(2023, 10, 31)
        self.new_date_14 = datetime(2023, 11, 8)
        self.new_date_15 = datetime(2023, 11, 13)
        self.test_date_start = datetime(2023, 11, 1)
        self.h5.complete_time_list.extend([self.new_date_15, self.new_date_14, self.new_date_13])
        self.assertEqual([3], analytics_module.habit_completion_counts([self.h5],
                                                                       self.test_date_start,
                                                                       datetime.today()),
                         "Habit completion count [weekly period] if start date of period starts in week "
                         "with already completed habit but completion date is before period start ")


class Test_Completion_Habits(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()
        self.test_date_start = datetime(2023, 12, 13)
        self.test_date_end = datetime(2023, 12, 30)

    def tearDown(self):
        self.habit_list.clear()

    def test_empty_list_input(self):
        self.assertEqual(([], [], [], [], [], []),
                         analytics_module.completions_habits([], self.test_date_start, self.test_date_end),
                         "Empty list as input -> no empty output")

    def test_no_habits_completed(self):
        habit_test = tracker.Habit("jogging", "daily")
        self.assertEqual(([0], [0], [0], [0], [0], [None]),
                         analytics_module.completions_habits([habit_test], self.test_date_start, self.test_date_end),
                         "Single habit with no habit completions")

    def test_actual_completions(self):
        self.test_date_end = datetime.today()
        self.assertEqual([6, 5, 5, 3, 6],
                         analytics_module.completions_habits(self.habit_list,
                                                             self.test_date_start,
                                                             self.test_date_end)[0],
                         "Actual completions for tracker_testing_data")

    def test_potential_completions_period(self):
        self.assertEqual([18, 3, 18, 3, 18],
                         analytics_module.completions_habits(self.habit_list,
                                                             self.test_date_start,
                                                             self.test_date_end)[1],
                         "Potential completions since period start for tracker_testing_data")

    def test_period_creation_date_relationship(self):
        self.test_date_start = datetime(2023, 9, 30)
        self.test_date_end = datetime(2023, 10, 29)
        self.assertEqual([1, 0, 3, 2, 1],
                         analytics_module.completions_habits(self.habit_list,
                                                             self.test_date_start,
                                                             self.test_date_end)[2],
                         "Relationship between period and creation date -> codes are not correct")

    def test_potential_completions_creation_date(self):
        self.assertEqual([83, 9, 130, 14, 63],
                         analytics_module.completions_habits(self.habit_list,
                                                             self.test_date_start,
                                                             self.test_date_end)[3],
                         "Potential completions since creation dates for tracker_testing_data")

    def test_potential_completions_period_creation_date(self):
        self.test_date_start = datetime(2023, 10, 1)
        self.assertEqual([83, 9, 91, 14, 63],
                         analytics_module.completions_habits(self.habit_list,
                                                             self.test_date_start,
                                                             self.test_date_end)[4],
                         "Potential completions since what is later "
                         "creation date or period start for tracker_testing_data")

    def test_potential_completion_percentage_period_creation_date(self):
        self.assertEqual([11, 66, 5, 0, 5],
                         analytics_module.completions_habits(self.habit_list,
                                                             self.test_date_start,
                                                             self.test_date_end)[5],
                         "Completion percentage since what is later "
                         "creation date or period start for tracker_testing_data")


class Test_Habit_Completion_Stats(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()
        self.test_date_start = datetime(2023, 11, 13)
        self.test_date_end = datetime(2023, 12, 30)

    def tearDown(self):
        self.habit_list.clear()

    def test_data_integrity(self):
        self.expected_result = [3, "Drinking at least two liters of water", "daily",
                                datetime.strptime("2023-08-23 00:00:00", "%Y-%m-%d %H:%M:%S"),
                                4, 48, 130, 50]
        self.test_result = analytics_module.habit_completion_stats(self.habit_list,
                                                                   self.test_date_start,
                                                                   self.test_date_end)
        result_list = list(self.test_result.itertuples())
        id = result_list[2][0]
        name = result_list[2].name
        period = result_list[2].period
        credate = result_list[2].credate
        act_complet = result_list[2].act_complet
        pot_complet_per = result_list[2].pot_complet_per
        pot_complet_credate = result_list[2].pot_complet_credate
        size = self.test_result.size
        self.test_result = [id, name, period, credate, act_complet, pot_complet_per, pot_complet_credate, size]

        self.assertEqual(self.expected_result, self.test_result, "Statistics on habit performance")


class Test_Performance(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()
        self.test_date_start = datetime(2023, 11, 1)
        self.test_date_end = datetime(2023, 12, 30)

    def tearDown(self):
        self.habit_list.clear()

    def test_best_performing_habits_daily(self):
        expected_result = (1, 5, 2)
        daily_list = tracker_util.filter_habit_list(self.habit_list, "daily")
        df = analytics_module.habit_completion_stats(daily_list, self.test_date_start, self.test_date_end)
        test_df = analytics_module.performance(df, "best")
        test_result = list(test_df.itertuples())
        id_1 = test_result[0][0]
        id_2 = test_result[1][0]
        num_elmnts = len(test_result)
        self.assertEqual(expected_result, (id_1, id_2, num_elmnts), "Best performing habits daily period")

    def test_best_performing_habits_weekly(self):
        expected_result = (4, 1)
        weekly_list = tracker_util.filter_habit_list(self.habit_list, "weekly")
        df = analytics_module.habit_completion_stats(weekly_list, self.test_date_start, self.test_date_end)
        test_df = analytics_module.performance(df, "best")
        test_result = list(test_df.itertuples())
        id_1 = test_result[0][0]
        num_elmnts = len(test_result)
        self.assertEqual(expected_result, (id_1, num_elmnts), "Best performing habits weekly period")

    def test_worst_performing_habits_daily(self):
        expected_result = (3, 1)
        daily_list = tracker_util.filter_habit_list(self.habit_list, "daily")
        df = analytics_module.habit_completion_stats(daily_list, self.test_date_start, self.test_date_end)
        test_df = analytics_module.performance(df, "worst")
        test_result = list(test_df.itertuples())
        id_1 = test_result[0][0]
        num_elmnts = len(test_result)
        self.assertEqual(expected_result, (id_1, num_elmnts), "Worst performing habits daily period")

    def test_worst_performing_habits_weekly(self):
        expected_result = (2, 1)
        weekly_list = tracker_util.filter_habit_list(self.habit_list, "weekly")
        df = analytics_module.habit_completion_stats(weekly_list, self.test_date_start, self.test_date_end)
        test_df = analytics_module.performance(df, "worst")
        test_result = list(test_df.itertuples())
        id_1 = test_result[0][0]
        num_elmnts = len(test_result)
        self.assertEqual(expected_result, (id_1, num_elmnts), "Worst performing habits weekly period")

    def test_overview_performing_habits_daily(self):
        expected_result = (3, 3)
        daily_list = tracker_util.filter_habit_list(self.habit_list, "daily")
        df = analytics_module.habit_completion_stats(daily_list, self.test_date_start, self.test_date_end)
        test_df = analytics_module.performance(df, "overview")
        test_result = list(test_df.itertuples())
        id_1 = test_result[2][0]
        num_elmnts = len(test_result)
        self.assertEqual(expected_result, (id_1, num_elmnts),
                         "Overview on performance: habits daily period")

    def test_overview_performing_habits_weekly(self):
        expected_result = (4, 2)
        weekly_list = tracker_util.filter_habit_list(self.habit_list, "weekly")
        df = analytics_module.habit_completion_stats(weekly_list, self.test_date_start, self.test_date_end)
        test_df = analytics_module.performance(df, "overview")
        test_result = list(test_df.itertuples())
        id_1 = test_result[0][0]
        num_elmnts = len(test_result)
        self.assertEqual(expected_result, (id_1, num_elmnts),
                         "Overview on performance: habits weekly period")


class Test_Streaks_Longest(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()

    def tearDown(self):
        self.habit_list.clear()

    def test_empty_list(self):
        test_result = analytics_module.streaks_longest([], "daily")
        expected_result = (0, [])
        self.assertEqual(expected_result, test_result,"Longest streaks empty input")

    def test_streak_daily(self):
        list_dates = self.habit_list[4].complete_time_list
        test_result = analytics_module.streaks_longest(list_dates, "daily")
        expected_result = [4, 2]
        self.assertEqual(expected_result, [test_result[0], len(test_result[1])], "Longest daily streaks")

    def test_streak_weekly(self):
        list_dates = self.habit_list[3].complete_time_list
        test_result = analytics_module.streaks_longest(list_dates, "weekly")
        expected_result = [4, 1]
        self.assertEqual(expected_result, [test_result[0], len(test_result[1])], "Longest weekly streaks")


class Test_Streaks_Current(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()

    def tearDown(self):
        self.habit_list.clear()

    def test_empty_input(self):
        test_result = analytics_module.streak_current([], "daily")
        self.assertEqual((0, None), test_result, "Current streak empty input")

    def test_streak_daily(self):
        list_dates = self.habit_list[0].complete_time_list
        test_result = analytics_module.streak_current(list_dates, "daily")
        expected_result = 4
        self.assertEqual(expected_result, test_result[0], "Current daily streak")

    def test_streak_weekly(self):
        list_dates = self.habit_list[1].complete_time_list
        test_result = analytics_module.streak_current(list_dates, "weekly")
        expected_result = 4
        self.assertEqual(expected_result, test_result[0], "Current weekly streak")


class Test_Habit_Streak_Stats(unittest.TestCase):

        def setUp(self):
            self.habit_list = tracker.Habit.habit_list
            tracker_testing_data.load_test_data()

        def tearDown(self):
            self.habit_list.clear()

        def test_empty_input(self):
            self.test_result = analytics_module.habit_streak_stats([])
            self.assertEqual(True, self.test_result.empty, "Statistics on habit streaks - empty input")

        def test_data_integrity(self):
            self.expected_result = [3, "Drinking at least two liters of water", "daily",
                                    datetime.strptime("2023-08-23 00:00:00", "%Y-%m-%d %H:%M:%S"),
                                    0, True, 2, 1, 40]
            self.test_result = analytics_module.habit_streak_stats(self.habit_list)
            result_list = list(self.test_result.itertuples())
            id = result_list[2][0]
            name = result_list[2].name
            period = result_list[2].period
            credate = result_list[2].credate
            cur_streak = result_list[2].streak_c_length
            cur_start = result_list[2].streak_c_date
            all_time_streak = result_list[2].streak_l_length
            all_time_dates = result_list[2].streak_l_dates
            size = self.test_result.size
            self.test_result = [id, name, period, credate, cur_streak,
                                isnull(cur_start), all_time_streak, len(all_time_dates), size]

            self.assertEqual(self.expected_result, self.test_result, "Statistics on habit streaks")


class Test_Streak_Data(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()

    def tearDown(self):
        self.habit_list.clear()

    def test_empty_input(self):
        df = analytics_module.streak_data(pd.DataFrame(), "current")
        self.assertEqual(True, df.empty, "Streak data - empty input")

    def test_daily_current(self):
        daily_list = tracker_util.filter_habit_list(self.habit_list, "daily")
        expected_result = 1
        df = analytics_module.habit_streak_stats(daily_list)
        test_result = list(analytics_module.streak_data(df, "current").itertuples())[0][0]
        self.assertEqual(expected_result, test_result, "Streak data for daily current streak")

    def test_weekly_current(self):
        weekly_list = tracker_util.filter_habit_list(self.habit_list, "weekly")
        expected_result = 2
        df = analytics_module.habit_streak_stats(weekly_list)
        test_result = list(analytics_module.streak_data(df, "current").itertuples())[0][0]
        self.assertEqual(expected_result, test_result, "Streak data for weekly current streak")

    def test_daily_longest(self):
        daily_list = tracker_util.filter_habit_list(self.habit_list, "daily")
        expected_result = 1
        df = analytics_module.habit_streak_stats(daily_list)
        test_result = list(analytics_module.streak_data(df, "longest").itertuples())[0][0]
        self.assertEqual(expected_result, test_result, "Streak data for daily longest streaks")

    def test_weekly_longest(self):
        weekly_list = tracker_util.filter_habit_list(self.habit_list, "weekly")
        expected_result = [2, 4, 2]
        df = analytics_module.habit_streak_stats(weekly_list)
        test_result_list = list(analytics_module.streak_data(df, "longest").itertuples())
        id_1 = test_result_list[0][0]
        id_2 = test_result_list[1][0]
        length = len(test_result_list)
        self.assertEqual(expected_result, [id_1, id_2, length], "Streak data for weekly longest streaks")


class Test_Completion_Dates_Statistics(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()

    def tearDown(self):
        self.habit_list.clear()

    def test_empty_input(self):
        h6 = tracker.Habit("h6", "weekly")
        self.assertEqual((), analytics_module.completion_dates_statistics(h6))

    def test_completion_dates_statistics(self):
        test_input = self.habit_list[0]
        self.assertEqual(5, len(analytics_module.completion_dates_statistics(test_input)[-1][11]))


class Test_Count_Completion_Dates_Statistics(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        tracker_testing_data.load_test_data()

    def tearDown(self):
        self.habit_list.clear()

    def test_empty_input(self):
        h6 = tracker.Habit("h6", "weekly")
        self.assertEqual((), analytics_module.count_completion_dates_statistics(h6))

    def test_completion_dates_statistics(self):
        test_input = self.habit_list[0]
        self.assertEqual(5, analytics_module.count_completion_dates_statistics(test_input)[-1][11])



if __name__ == '__main__':
    unittest.main()
