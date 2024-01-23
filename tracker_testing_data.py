from datetime import datetime, timedelta
import tracker
import databaseSQL
import tracker_util


def load_test_data():
    """Loads test data into memory:

    Expected results:

    1. Taking a walk: not complete, 4 current streak, 5 longest streak Dec 10-14, 9 completions
    2. Jogging 5k: complete, 4 current streak == longest streak, 6 completions
    3. Drinking: not complete, no current streak, 2 longest streak Dec 12-13, 8 completions
    4. Vitamin D: complete, 3 current streak, 4 longest streak Nov 2-23, 8 completions
    5. Reading: complete, 1 current streak, 2x 4 longest streaks Dec 10-13 & 2-days-ago - 5-days-ago, 10 completions

    Longest daily streak ever: Taking a walk, 5 periods, Dec 10-14

    Longest daily streak currently: Taking a walk, 4 periods

    Longest weekly streak ever: 4 periods: jogging -> current streak; Vitamin D, Dec 2-23

    Longest weekly streak currently: Jogging, 4 periods

    Total completions: 41
    """
    h1 = tracker.Habit("Taking a walk around the neighborhood", "daily", creation_date="2023-10-09 00:00:00")
    h2 = tracker.Habit("Jogging 5km", "weekly", creation_date="2023-11-01 00:00:00")
    h3 = tracker.Habit("Drinking at least two liters of water", "daily", creation_date="2023-08-23 00:00:00")
    h4 = tracker.Habit("Vitamin D supplement", "weekly", creation_date="2023-09-30 00:00:00")
    h5 = tracker.Habit("Reading for 1 hour", "daily", creation_date="2023-10-29 00:00:00")
    # for h1
    # enter oldest data first
    new_date_1 = datetime.now() - timedelta(days=1)
    new_date_2 = datetime.now() - timedelta(days=2)
    new_date_3 = datetime.now() - timedelta(days=3)
    new_date_4 = datetime.now() - timedelta(days=4)
    insert_test_date_into_habit(h1, datetime(2023, 12, 10))
    insert_test_date_into_habit(h1, datetime(2023, 12, 11))
    insert_test_date_into_habit(h1, datetime(2023, 12, 12))
    insert_test_date_into_habit(h1, datetime(2023, 12, 13))
    insert_test_date_into_habit(h1, datetime(2023, 12, 14))
    insert_test_date_into_habit(h1, new_date_4)
    insert_test_date_into_habit(h1, new_date_3)
    insert_test_date_into_habit(h1, new_date_2)
    insert_test_date_into_habit(h1, new_date_1)
    # for h2
    new_date_1 = datetime.now() - timedelta(days=0)
    new_date_2 = datetime.now() - timedelta(days=7)
    new_date_3 = datetime.now() - timedelta(days=14)
    new_date_4 = datetime.now() - timedelta(days=21)
    insert_test_date_into_habit(h2, datetime(2023, 12, 8))
    insert_test_date_into_habit(h2, datetime(2023, 12, 10))
    insert_test_date_into_habit(h2, datetime(2023, 12, 12))
    insert_test_date_into_habit(h2, datetime(2023, 12, 13))
    insert_test_date_into_habit(h2, new_date_4)
    insert_test_date_into_habit(h2, new_date_3)
    insert_test_date_into_habit(h2, new_date_2)
    insert_test_date_into_habit(h2, new_date_1)
    # for h3
    new_date_1 = datetime.now() - timedelta(days=2)
    new_date_2 = datetime.now() - timedelta(days=5)
    new_date_3 = datetime.now() - timedelta(days=12)
    new_date_4 = datetime.now() - timedelta(days=19)
    insert_test_date_into_habit(h3, datetime(2023, 12, 8))
    insert_test_date_into_habit(h3, datetime(2023, 12, 10))
    insert_test_date_into_habit(h3, datetime(2023, 12, 12))
    insert_test_date_into_habit(h3, datetime(2023, 12, 13))
    insert_test_date_into_habit(h3, new_date_4)
    insert_test_date_into_habit(h3, new_date_3)
    insert_test_date_into_habit(h3, new_date_2)
    insert_test_date_into_habit(h3, new_date_1)
    # for h4
    new_date_1 = datetime.now() - timedelta(days=0)
    new_date_2 = datetime.now() - timedelta(days=7)
    new_date_3 = datetime.now() - timedelta(days=10)
    new_date_4 = datetime.now() - timedelta(days=14)
    insert_test_date_into_habit(h4, datetime(2023, 11, 2))
    insert_test_date_into_habit(h4, datetime(2023, 11, 9))
    insert_test_date_into_habit(h4, datetime(2023, 11, 13))
    insert_test_date_into_habit(h4, datetime(2023, 11, 23))
    insert_test_date_into_habit(h4, datetime(2023, 12, 4))
    insert_test_date_into_habit(h4, new_date_4)
    insert_test_date_into_habit(h4, new_date_3)
    insert_test_date_into_habit(h4, new_date_2)
    insert_test_date_into_habit(h4, new_date_1)
    # for h5
    new_date_1 = datetime.now() - timedelta(days=0)
    new_date_2 = datetime.now() - timedelta(days=2)
    new_date_3 = datetime.now() - timedelta(days=3)
    new_date_4 = datetime.now() - timedelta(days=4)
    new_date_5 = datetime.now() - timedelta(days=5)
    insert_test_date_into_habit(h5, datetime(2023, 12, 8))
    insert_test_date_into_habit(h5, datetime(2023, 12, 10))
    insert_test_date_into_habit(h5, datetime(2023, 12, 11))
    insert_test_date_into_habit(h5, datetime(2023, 12, 12))
    insert_test_date_into_habit(h5, datetime(2023, 12, 12))
    insert_test_date_into_habit(h5, datetime(2023, 12, 13))
    insert_test_date_into_habit(h5, new_date_5)
    insert_test_date_into_habit(h5, new_date_4)
    insert_test_date_into_habit(h5, new_date_3)
    insert_test_date_into_habit(h5, new_date_2)
    insert_test_date_into_habit(h5, new_date_1)


def load_test_data_to_db() -> None:
    """Creates database file with test data"""
    # load test data into memory
    load_test_data()
    # delete database if exists
    tracker_util.delete_file("user_data")
    # create new database
    databaseSQL.create_db()
    # save data from memory to database
    databaseSQL.object_to_db()
    # delete data from memory
    tracker.Habit.habit_list.clear()


def insert_test_date_into_habit(habit, indate):
    """Simulates regular entry of testing data on given date"""
    # complete habit
    habit.complete_habit(indate)


if __name__ == '__main__':
    load_test_data_to_db()
