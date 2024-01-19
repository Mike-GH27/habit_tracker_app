import unittest
import os
import sys
import tracker_testing_data
from datetime import timedelta, datetime, date

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import tracker_util
import tracker


class Test_Days_Difference(unittest.TestCase):

    def test_one_day_gap(self):
        date1 = datetime.now()
        date2 = datetime.now() - timedelta(days=1)
        days_difference = tracker_util.days_difference(date1, date2)
        self.assertEqual(1, days_difference, "Difference in days is not correct if there is an actual gap")

    def test_same_day(self):
        date1 = datetime.today()
        date2 = datetime.today()
        days_difference = tracker_util.days_difference(date1, date2)
        self.assertEqual(0, days_difference, "Difference in days is not correct if there is no actual gap")


class Test_Long_Year(unittest.TestCase):

    def test_no_long_year(self):
        self.assertEqual(False, tracker_util.is_long_year(2023),
                         "Returns it is a long year even though it is not")

    def test_long_year(self):
        self.assertEqual(True, tracker_util.is_long_year(2004),
                         "Returns it is not a long year even though it is")


class Test_Date_Type_Conversion(unittest.TestCase):

    def test_wrong_input_error(self):
        """Used format: %Y-%m-%d %H:%M:%S"""
        with self.assertRaises(ValueError,
                               msg="Does not recognize wrong input and/or does not throw ValueError Exception"):
            tracker_util.indate_type_conversion("2020,12,10 12:30:45")

    def test_string_as_input(self):
        """Used format: %Y-%m-%d %H:%M:%S"""
        self.input_string = "2020-12-10 12:30:45"
        self.test_date = datetime(2020, 12, 10, 12, 30, 45)
        self.assertEqual(self.test_date, tracker_util.indate_type_conversion(self.input_string),
                         "String conversion fails")

    def test_date_object_as_input(self):
        self.date_object = date(2020, 12, 10)
        self.test_date = datetime(2020, 12, 10)
        self.assertEqual(self.test_date, tracker_util.indate_type_conversion(self.date_object),
                         "Date object conversion fails")


class Date_Conversion(unittest.TestCase):

    def setUp(self):
        self.date1 = datetime(2000, 3, 10, second=22)
        self.date2 = datetime(2100, 2, 20, minute=12)
        self.date3 = datetime(2200, 1, 30, microsecond=420)
        self.test_list = [self.date1, self.date2, self.date3]

    def test_date_conversion_attribute_elimination(self):
        check_sum = 0
        self.assertEqual(check_sum, sum([tracker_util.date_conversion(self.test_list)[1].minute,
                                tracker_util.date_conversion(self.test_list)[1].minute,
                                tracker_util.date_conversion(self.test_list)[1].minute]))

    def test_date_conversion_attribute_conservation(self):
        self.check_sum = 2000 + 2 + 30
        self.assertEqual(self.check_sum, sum([tracker_util.date_conversion(self.test_list)[0].year,
                                tracker_util.date_conversion(self.test_list)[1].month,
                                tracker_util.date_conversion(self.test_list)[2].day]))


class Test_Get_Date_String(unittest.TestCase):

    def test_datetime_to_string_format(self):
        self.datetime_object = datetime(year=2023, month=10, day=12)
        self.test_string = "[October, 12, '23]"
        self.assertEqual(self.test_string, tracker_util.get_date_string(self.datetime_object),
                         "Datetime object does not get converted to string in required formatting correctly")


class Test_Day_Streak(unittest.TestCase):

    def test_no_streak_none_objects(self):
        self.assertEqual(0, tracker_util.day_streak(None, None),
                         'Does not compute daily streak properly '
                         'if there is no streak / input is None objects in tuple')

    def test_one_day_streak(self):
        self.test_date = datetime.today()
        self.assertEqual(1, tracker_util.day_streak(self.test_date, self.test_date),
                         "Does not compute daily streak correctly if streak is only one day")

    def test_multiple_day_streak(self):
        self.test_date_end = datetime.today()
        self.test_date_start = datetime.today() - timedelta(days=4)
        self.assertEqual(5, tracker_util.day_streak(self.test_date_start, self.test_date_end),
                         'Does not compute daily streak correctly if streak is >1')


class Test_Week_Streak(unittest.TestCase):

    def test_no_streak_none_objects(self):
        self.assertEqual(0, tracker_util.week_streak(None, None),
                         'Does not compute weekly streak properly '
                         'if there is no streak / input is None objects in tuple')

    def test_one_week_streak(self):
        self.test_date = datetime.today()
        self.assertEqual(1, tracker_util.week_streak(self.test_date, self.test_date),
                         'Does not compute weekly streak properly if there is a one week streak')

    def test_multiple_week_streak(self):
        self.test_date_end = datetime.today()
        self.test_date_start = datetime.today() - timedelta(days=28)
        self.assertEqual(5, tracker_util.week_streak(self.test_date_end, self.test_date_start),
                         'Does not compute weekly streak properly if there is a streak >1')

    def test_streak_between_adjacent_years_no_long_year(self):
        self.test_date_end = datetime(year=2023, month=1, day=9)
        self.test_date_start = datetime(year=2022, month=12, day=26)
        self.assertEqual(3, tracker_util.week_streak(self.test_date_start, self.test_date_end),
                         'Does not compute weekly streak properly '
                         'if there is a streak between adjacent years -> no long year')

    def test_streak_between_adjacent_years_long_year_case(self):
        self.test_date_end = datetime(year=2005, month=1, day=11)
        self.test_date_start = datetime(year=2004, month=12, day=22)
        self.assertEqual(4, tracker_util.week_streak(self.test_date_start, self.test_date_end),
                         'Does not compute weekly streak properly '
                         'if there is a streak between adjacent years -> long year')

    def test_streak_between_more_than_2_years_no_long_year(self):
        self.test_date_end = datetime(year=2023, month=1, day=16)
        self.test_date_start = datetime(year=2021, month=12, day=24)
        self.assertEqual(57, tracker_util.week_streak(self.test_date_start, self.test_date_end),
                         'Does not compute weekly streak properly '
                         'if there is a streak across entire years -> no long year')

    def test_streak_between_more_than_2_years_long_year_between_case(self):
        self.test_date_end = datetime(year=2005, month=1, day=18)
        self.test_date_start = datetime(year=2003, month=12, day=23)
        self.assertEqual(57, tracker_util.week_streak(self.test_date_start, self.test_date_end),
                         'Does not compute day streak properly '
                         'if there is a streak across entire years -> long year')


class Test_Filter_Period_Habit(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        self.habit_list.clear()
        self.h1 = tracker.Habit("h1", "daily")
        self.h2 = tracker.Habit("h2", "daily")
        self.h3 = tracker.Habit("h3", "weekly")
        self.h4 = tracker.Habit("h4", "weekly")
        self.h5 = tracker.Habit("h5", "daily")
        self.h6 = tracker.Habit("h6", "weekly")
        self.h7 = tracker.Habit("h7", "weekly")

    def tearDown(self):
        self.habit_list.clear()

    def test_filter_daily(self):
        daily_elements = len(tracker_util.filter_habit_list(self.habit_list, "daily"))
        self.assertEqual(3, daily_elements, 'Filter does not work for daily habits')

    def test_filter_weekly(self):
        weekly_elements = len(tracker_util.filter_habit_list(self.habit_list, "weekly"))
        self.assertEqual(4, weekly_elements, 'Filter does not work for weekly habits')


class Test_Filter_From_Date(unittest.TestCase):

    def setUp(self):
        self.new_date_1 = datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
        self.new_date_2 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=1))
        self.new_date_3 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=2))
        self.new_date_4 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=3))
        self.new_date_5 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=4))
        self.new_date_6 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=6))
        self.new_date_7 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=7))
        self.new_date_8 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=12))
        self.new_date_9 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                           - timedelta(days=14))
        self.new_date_10 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                            - timedelta(days=21))
        self.new_date_11 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                            - timedelta(days=28))
        self.new_date_12 = (datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
                            - timedelta(days=35))
        self.list_test = [self.new_date_1, self.new_date_2, self.new_date_3, self.new_date_4, self.new_date_5,
                               self.new_date_6, self.new_date_7, self.new_date_8, self.new_date_9,
                               self.new_date_10, self.new_date_11, self.new_date_12]

    def test_empty_list(self):
        self.list_test = []
        self.assertEqual([], tracker_util.filter_from_date(self.list_test, self.new_date_12),
                         "Date filter does not process an empty input list correctly")

    def test_filter_today_before(self):
        self.assertEqual(1, len(tracker_util.filter_from_date(self.list_test, self.new_date_1, "before")),
                         "Date filter does not filter out correct number of smaller elements "
                         "if cut-off date is first element of list")

    def test_filter_today_after(self):
        self.assertEqual(12, len(tracker_util.filter_from_date(self.list_test, self.new_date_1, "after")),
                         "Date filter does not filter out correct number of larger elements "
                         "if cut-off date is first element of list")

    def test_filter_day_between_before(self):
        self.assertEqual(8, len(tracker_util.filter_from_date(self.list_test, self.new_date_8, "before")),
                         "Date filter does not filter out correct number of smaller elements "
                         "if cut-off date is element of list and not end- or start-point")

    def test_filter_day_between_after(self):
        self.assertEqual(5, len(tracker_util.filter_from_date(self.list_test, self.new_date_8, "after")),
                         "Date filter does not filter out correct number of larger elements "
                         "if cut-off date is element of list and not end- or start-point")

    def test_filter_day_end_before(self):
        self.assertEqual(12, len(tracker_util.filter_from_date(self.list_test, self.new_date_12, "before")),
                         "Date filter does not filter out correct number of smaller elements "
                         "if cut-off date is last element of list")

    def test_filter_day_end_after(self):
        self.assertEqual(1, len(tracker_util.filter_from_date(self.list_test, self.new_date_12, "after")),
                         "Date filter does not filter out correct number of larger elements "
                         "if cut-off date is last element of list")

    def test_filter_today_value_before(self):
        self.assertEqual(self.new_date_1, tracker_util.filter_from_date(self.list_test, datetime.today(),
                                                                          "before")[0],
                         "Date filter in before mode does not return correct date "
                         "if cut-off date is first element of list")

    def test_filter_today_value_after(self):
        self.assertEqual(self.new_date_1, tracker_util.filter_from_date(self.list_test, datetime.today(), "after")[0],
                         "Date filter in after mode "
                         "does not return correct date if cut-off date is first element of list")

    def test_filter_day_between_end_points_before(self):
        self.assertEqual(self.new_date_8, tracker_util.filter_from_date(self.list_test, self.new_date_8, "before")[-1],
                         "Date filter in before mode does not return correct date "
                         "if cut-off date is element of list and not end- or start-point")

    def test_filter_day_between_end_points_after(self):
        self.assertEqual(self.new_date_12, tracker_util.filter_from_date(self.list_test, self.new_date_8, "after")[-1],
                         "Date filter in after mode does not return correct date "
                         "if cut-off date is element of list and not end- or start-point")

    def test_filter_day_between_values_before(self):
        self.assertEqual(self.new_date_8, tracker_util.filter_from_date(self.list_test,
                                                                        self.new_date_8 - timedelta(days=1),
                                                                        "before")[-1],
                         "Date filter in before mode does not return correct date "
                         "if cut-off date is between elements of list")

    def test_filter_day_between_values_after(self):
        self.assertEqual(self.new_date_8, tracker_util.filter_from_date(self.list_test,
                                                                        self.new_date_8 + timedelta(days=1),
                                                                        "after")[0],
                         "Date filter in after mode does not return correct date "
                         "if cut-off date is between elements of list")

    def test_filter_day_smallest_value_before(self):
        self.assertEqual(12, len(tracker_util.filter_from_date(self.list_test, self.new_date_12, "before")),
                         "Date filter in before mode does not return correct number of elements "
                         "if cut-off date is smallest element of list")

    def test_filter_day_smallest_value_after(self):
        self.assertEqual(1, len(tracker_util.filter_from_date(self.list_test, self.new_date_12, "after")),
                         "Date filter in after mode does not return correct number of elements "
                         "if cut-off date is smallest element of list")

    def test_filter_day_largest_value_before(self):
        self.assertEqual(1, len(tracker_util.filter_from_date(self.list_test, self.new_date_1, "before")),
                         "Date filter in before mode does not return number of elements "
                         "if cut-off date is largest element of list")

    def test_filter_day_largest_value_after(self):
        self.assertEqual(12, len(tracker_util.filter_from_date(self.list_test, self.new_date_1, "after")),
                         "Date filter in after mode does not return correct number of elements "
                         "if cut-off date is largest element of list")

    def test_filter_day_larger_than_list_min_before(self):
        self.assertEqual(0, len(tracker_util.filter_from_date(self.list_test,
                                                              self.new_date_1 + timedelta(days=10),
                                                              "before")),
                         "Date filter in before mode does not return correct number of zero elements "
                         "if cut-off date is larger than any element of list")

    def test_filter_day_smaller_than_list_min_after(self):
        self.assertEqual(0, len(tracker_util.filter_from_date(self.list_test,
                                                              self.new_date_12 - timedelta(days=10),
                                                              "after")),
                         "Date filter in after mode does not return correct number of zero elements "
                         "if cut-off date is smaller than any element of list")


class Test_get_earliest_Creation_Date(unittest.TestCase):

    def setUp(self):
        tracker_testing_data.load_test_data()
        self.habit_list = tracker.Habit.habit_list

    def tearDown(self):
        self.habit_list.clear()

    def test_empty_input(self):
        self.assertEqual(datetime.min, tracker_util.get_earliest_creation_date([]),
                         "Earliest creation date - empty input")

    def test_earliest_creation_date(self):
        self.assertEqual(datetime(2023, 8, 23),
                         tracker_util.get_earliest_creation_date(self.habit_list))





if __name__ == '__main__':
    unittest.main()
