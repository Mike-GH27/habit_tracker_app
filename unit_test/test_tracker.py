import unittest
import sys
import os
from datetime import datetime, timedelta, date

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import tracker


class Test_Habit_Initializer_Habit_Id(unittest.TestCase):

    def setUp(self):
        self.h1 = tracker.Habit("Habit_1", "daily")
        self.h2 = tracker.Habit("Habit_2", "daily")
        self.h3 = tracker.Habit("Habit_3", "daily")
        self.h4 = tracker.Habit("Habit_4", "daily")
        self.habit_list = tracker.Habit.habit_list

    def tearDown(self):
        self.habit_list.clear()

    def test_unique_ID_subsequent(self):
        self.h5 = tracker.Habit("Habit_5", "daily")
        self.assertEqual(5, self.habit_list[4].habit_id, "Subsequent assignment of "
                                                         "habit_ids is not working")

    def test_unique_habit_ID_after_deletion(self):
        del self.habit_list[2]
        self.h5 = tracker.Habit("Habit_5", "daily")
        self.assertEqual(3, self.habit_list[3].habit_id, "Assignment of unique habit_ids after deletion"
                                                         "is not working")


class Test_Habit_Initializer_Input_Date_Type_Conversion(unittest.TestCase):

    def tearDown(self):
        self.habit_list = tracker.Habit.habit_list
        self.habit_list.clear()

    def test_wrong_input_error(self):
        """Used format: %Y-%m-%d %H:%M:%S"""
        with self.assertRaises(ValueError, msg="Does not recognize wrong input of date"):
            self.h1 = tracker.Habit("habit_1", "daily", creation_date="2020,12,10 12:30:45")

    def test_string_as_input(self):
        """Used format: %Y-%m-%d %H:%M:%S"""
        self.h1 = tracker.Habit("habit_1", "daily", creation_date="2020-12-10 12:30:45")
        self.test_date = datetime(2020, 12, 10, 12, 30, 45)
        self.assertEqual(self.test_date, self.h1.creation_date, "String conversion fails of date")

    def test_date_object_as_input(self):
        self.test_date_object = date(2020, 12, 10)
        self.h1 = tracker.Habit("habit_1", "daily", creation_date=self.test_date_object)
        self.test_date = datetime(2020, 12, 10)
        self.assertEqual(self.test_date, self.h1.creation_date, "Date object conversion fails of date")


class Test_Complete_Habit(unittest.TestCase):

    def setUp(self):
        self.habit_list = tracker.Habit.habit_list
        self.h1 = tracker.Habit("h1", "daily")
        self.h2 = tracker.Habit("h2", "weekly")

    def tearDown(self):
        self.habit_list.clear()

    def test_complete_daily_when_completed(self):
        date1 = datetime.today()
        self.h1.complete_time_list.append(date1)
        self.assertEqual(False, self.h1.complete_habit(),
                         "Completes daily habit even though already completed")

    def test_complete_weekly_when_completed(self):
        date1 = datetime.today()
        self.h2.complete_time_list.append(date1)
        self.assertEqual(False, self.h2.complete_habit(),
                         "Completes weekly habit even though already completed")

    def test_complete_daily_when_not_completed(self):
        date1 = datetime.today() - timedelta(days=1)
        self.h1.complete_time_list.append(date1)
        self.assertEqual(True, self.h1.complete_habit(),
                         "Does not complete daily habit even though not completed")

    def test_complete_weekly_when_not_completed(self):
        date1 = datetime.today() - timedelta(days=7)
        self.h2.complete_time_list.append(date1)
        self.assertEqual(True, self.h1.complete_habit(),
                         "Does not complete weekly habit even though not completed")


if __name__ == '__main__':
    unittest.main()
