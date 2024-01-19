from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, insert
import datetime
import shutil
import os
import tracker
import tracker_util
import tracker_testing_data
from datetime import datetime


def create_db(db_name='sqlite:///user_data.db') -> None:
    """creates database with specified name
    :param string db_name: name of database
    """
    engine = create_engine(db_name, echo=False)
    meta.create_all(engine)
    engine.dispose()


def insert_data_habits(inhabit_id, inhabit, inperiod, increation_date, db_name='sqlite:///user_data.db') -> None:
    """Inserts data into habits_table. Input variables correspond to columns in table. increation_date must be
    datetime object or string in YY-MM-DD HH:MM:SS format
    :param int inhabit_id:
    :param string inhabit:
    :param string inperiod:
    :param datetime|string increation_date:
    :param string db_name: """
    # connects to database file in install directory
    engine = create_engine(db_name, echo=False)
    conn = engine.connect()
    # converts input for creation_date into string if input is datetime object
    if isinstance(increation_date, datetime):
        increation_date = increation_date.strftime('%Y-%m-%d %H:%M:%S')
    ins = insert(habits).values(habit_id=inhabit_id, habit=inhabit, period=inperiod, creation_date=increation_date)
    conn.execute(ins)
    conn.commit()
    conn.close()
    engine.dispose()


def insert_complete_time_list(indate, inhabit_id, db_name='sqlite:///user_data.db') -> None:
    """Inserts data into habit_completed_list. Input variables correspond to columns in table. indaten_date must be
    datetime object or string in YY-MM-DD HH:MM:SS format
    :param datetime|str indate:
    :param int inhabit_id:
    :param str db_name: """
    # connects to database file in install directory
    engine = create_engine(db_name, echo=False)
    conn = engine.connect()
    # converts input datetime object into string as SQLite does not accept datetime objects
    if isinstance(indate, datetime):
        indate = indate.strftime('%Y-%m-%d %H:%M:%S')
    ins = insert(complete_time_list).values(date=indate, habit_id=inhabit_id)
    conn.execute(ins)
    conn.commit()
    conn.close()
    engine.dispose()


def read_data_habits(db_name='sqlite:///user_data.db'):
    """Reads all data from habits table in database.

    Column1: habit_id, column2: habit, column3: period, column4: creation date
    :param str db_name: database name
    :return: list[tuple[]]: list item represent rows and
    index position in tuple represent columns

    column1: habit_id, column2: habit name: column3: period, column4: creation date"""
    # connects to database file in install directory
    engine = create_engine(db_name, echo=False)
    conn = engine.connect()
    select = habits.select()
    result = conn.execute(select)
    row = result.fetchall()
    conn.close()
    engine.dispose()
    return row


def read_complete_time_list(habit_id, db_name='sqlite:///user_data.db'):
    """Reads data from complete_time_list table in database where habit_id matches input parameter

    :param int habit_id:
    :param str db_name:
    :return: list[tuple[]]: list of tuples where list item represent rows and
    index position in tuple represent columns

    column1: id, column2: completion date, column3: habit_id"""
    # connects to database file in install directory
    engine = create_engine(db_name, echo=False)
    conn = engine.connect()
    select = complete_time_list.select().where(complete_time_list.c.habit_id == f"{habit_id}")
    result = conn.execute(select)
    row = result.fetchall()
    conn.close()
    engine.dispose()
    return row


def object_to_db(db_name='sqlite:///user_data.db', file_name_1="user_data.db") -> None:
    """Inserts data from habit_list into database
    :param db_name: name of database
    :param file_name_1: name of database file
    """
    # save data in separate file in case something goes wrong
    try:
        if os.path.isfile(file_name_1):
            shutil.copyfile(file_name_1, "user_data_temp.db")
        else:
            pass
        tracker_util.delete_file(file_name_1)
        create_db(db_name)
        hl = tracker.Habit.habit_list
        for i in range(len(hl)):
            insert_data_habits(hl[i].habit_id, hl[i].habit_name, hl[i].period, hl[i].creation_date, db_name=db_name)
            for b in range(len(hl[i].complete_time_list)):
                hcl = hl[i].complete_time_list
                insert_complete_time_list(hcl[b], hl[i].habit_id, db_name=db_name)
    except Exception as error:
        if os.path.isfile("user_data_temp.db"):
            shutil.copyfile("user_data_temp.db", file_name_1)
        print('data could not be saved due to an error')
        print(error)
    finally:
        tracker_util.delete_file("user_data_temp.db")


def db_to_object(db_name='sqlite:///user_data.db') -> None:
    """Creating list of habit objects from database
    :param str db_name: database name
    """
    tuhabits = read_data_habits(db_name)
    tracker.Habit.habit_list.clear()
    for x in range(len(tuhabits)):
        # convert strings from database into datetime object
        # 3 refers to column creation_date
        tempdate1 = tuhabits[x][3]
        tempdate1 = datetime.strptime(tempdate1, '%Y-%m-%d %H:%M:%S')
        tracker.Habit(tuhabits[x][1], tuhabits[x][2], tempdate1, tuhabits[x][0])
        tuple_time_complete_list = read_complete_time_list(tuhabits[x][0], db_name)
        for b in range(len(tuple_time_complete_list)):
            # b is for row and 1 for date column
            # Conversion from date to datetime object
            tempdate_2 = tuple_time_complete_list[b][1]
            tempdate_2 = datetime.strptime(tempdate_2, '%Y-%m-%d %H:%M:%S')
            tracker.Habit.habit_list[x].complete_time_list.append(tempdate_2)


def app_load_data_base(file_name_1="user_data.db") -> None:
    """Creates list of habit objects from database: creates database if it does not exist
    :param str file_name_1: file name of database
    """
    if not os.path.isfile(file_name_1):
        create_db()
        return
    db_to_object()


meta = MetaData()
habits = Table('habits', meta,
               Column('habit_id', Integer, primary_key=True),
               Column('habit', String),
               Column('period', String),
               Column('creation_date', String),
               )

complete_time_list = Table('complete_time_list', meta,
                           Column('id', Integer, primary_key=True),
                           Column('date', String),
                           Column('habit_id', Integer, ForeignKey('habits.habit_id')))


if __name__ == '__main__':
    pass
