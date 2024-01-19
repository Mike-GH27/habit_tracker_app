import os
import sys
import unittest
import tempfile
import tracker_testing_data

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import databaseSQL
import tracker


class Test_Data_Base_Reading_Writing(unittest.TestCase):

    def test_writing_reading_habit_data(self):
        db_name = tempfile.NamedTemporaryFile(suffix=".db").name
        databaseSQL.create_db(db_name=f'sqlite:///{db_name}')
        tracker_testing_data.load_test_data()
        databaseSQL.object_to_db(file_name_1=f"{db_name}.db", db_name=f'sqlite:///{db_name}')
        data = databaseSQL.read_data_habits(db_name=f'sqlite:///{db_name}')
        self.assertEqual("Taking a walk around the neighborhood",
                         data[0][1], "Writing or reading habit data from/to database does not work correctly")

    def test_writing_reading_complete_time_data(self):
        db_name = tempfile.NamedTemporaryFile(suffix=".db").name
        databaseSQL.create_db(db_name=f'sqlite:///{db_name}')
        tracker_testing_data.load_test_data()
        test = tracker.Habit.habit_list[0].complete_time_list[0]
        test = test.strftime('%Y-%m-%d %H:%M:%S')
        databaseSQL.object_to_db(file_name_1=f"{db_name}.db", db_name=f'sqlite:///{db_name}')
        data = databaseSQL.read_complete_time_list(1, db_name=f'sqlite:///{db_name}')
        self.assertEqual(test,
                         data[0][1],
                         "Writing or reading complete time data from/to database does not work correctly")


if __name__ == '__main__':
    unittest.main()
