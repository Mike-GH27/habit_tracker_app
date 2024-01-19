from datetime import datetime
import tracker_util


class Habit:
    """
    Class for creating habit object with information about the habit, a list of all habits as a class attribute and
    different methods to alter completion data and check completion status
    
    Habit object gets appended to class attribute habit_list automatically upon initialization

    :param string habit_name: name of habit
    :param string period: period of habit [daily, weekly]
    :param datetime creation_date: date when habit was created
    :param int habit_id: unique id

    Further attributes:

    complete_time_list: list of datetime objects: when habit was completed, latest item in list is most recent one
    """
    # class attribute where all habit objects are stored
    habit_list = []

    def __init__(self, habit_name, period, creation_date=datetime.now(), habit_id=None):
        self.habit_name = habit_name
        self.period = period
        # type check and conversion for creation_date
        self.creation_date = tracker_util.indate_type_conversion(creation_date)
        self.habit_id = habit_id
        # determine unique habit_id if habit_id is None (default case), otherwise uniqueness is assumed
        if self.habit_id is None:
            # Determining next free habit_id for new object. It is assumed that list from database has been loaded if it
            # exists
            # if list is empty and new habit object is the first one to be defined
            if not Habit.habit_list:
                self.habit_id = 1
            # if there is an empty habit_id spot between values
            else:
                Habit.habit_list.sort(key=lambda x: x.habit_id, reverse=False)
                for i in range(len(Habit.habit_list)):
                    if (i + 1) != Habit.habit_list[i].habit_id:
                        self.habit_id = i + 1
                        break
                # if only empty spot is at end of list
                if self.habit_id is None:
                    self.habit_id = len(Habit.habit_list) + 1
        self.complete_time_list = []
        # adds new Habit object to class list
        Habit.habit_list.append(self)

    def clear_tracking_data(self) -> None:
        """Resets tracking data by clearing completion dates from complete_time_list"""
        self.complete_time_list.clear()

    def check_complete_status(self, indate=datetime.today()) -> bool:
        """Checks if last completion of habit has been completed in given period. (Note: methods only checks for the
        latest completed period of the habit)

        Returns: boolean
        :param datetime indate: date for which completion status should be checked
        :return: bool"""
        if self.period == "daily":
            if not self.complete_time_list:
                return False
            elif tracker_util.days_difference(self.complete_time_list[-1], indate) > 0:
                return False
            else:
                return True

        elif self.period == "weekly":
            if not self.complete_time_list:
                return False
            elif tracker_util.week_streak(self.complete_time_list[-1], indate) > 1:
                return False
            else:
                return True

    def complete_habit(self, indate=datetime.now()) -> bool:
        """Checks if habit has already been completed and appends complete_time_list if not

        :param datetime indate: date at which habit is completed
        :return: bool: True if completion was valid, False if habit was already completed in current period"""
        if self.check_complete_status(indate):
            return False
        else:
            self.complete_time_list.append(indate)
            return True


if __name__ == '__main__':
    pass
