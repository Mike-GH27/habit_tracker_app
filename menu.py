import analytics_module
import tracker_util
import click
import databaseSQL
import tracker
import tracker_testing_data
import calendar
import os
from datetime import datetime, timedelta


# auxiliary variables
global_menu_block = {
    "line": "-----------------------------------------------------",
    "daily_line": "---------------------Daily---------------------------",
    "weekly_line": "---------------------Weekly--------------------------",
    "Streaks": "----------------------Streaks------------------------",
    "Performance": "------------------Performance------------------------",
    "Performance_Settings": "---------------Performance settings------------------",
    "Preset_Options": "----------------Preset options-----------------------",
    "Custom_Options": "----------------Custom options-----------------------",
    "Analysis": "------------------------Analysis---------------------",
    "Habit_Ranking": "-------------------Habit Ranking---------------------"
}
global_dict = {}
global_dict_2 = {}
global_period_options = {
    "this_week": "this week",
    "past_7_days": "past 7 days",
    "this_month": "this month",
    "past_30_days": "past 30 days",
    "beginning_last_month": "since beginning of last month",
    "past_12_weeks": "past 12 weeks",
    "beginning_last_quarter": "since beginning of last quarter",
    "this_year": "this year",
    "past_365_days": "past 365 days",
    "custom_period_days": "custom period (days)",
    "custom_period_weeks": "custom period (weeks)",
    "custom_date": "custom date",
    "default": "default: since creation date of first tracked habit"}
global_variables = {
    # daily or weekly
    "period": "None",
    # period number [int]
    "period_number": 0,
    # start date
    "date_start": datetime.today(),
    # end date
    "date_end": datetime.today(),
    # period description
    "descr": global_period_options["default"],
    # custom period chosen by user format: last <number> of <day(s) or week(s)>
    "custom_period": "",
    # threshold of potential completions in period for inclusion - daily
    "completion_threshold_daily": 30,
    # threshold of potential completions in period for inclusion - weekly
    "completion_threshold_weekly": 10
}


def main_menu() -> None:
    """Main menu. User interface app_main_menu gets called separately"""
    print_app_heading()
    click.echo(" Main Menu")
    click.echo(global_menu_block["line"])
    click.echo(" 1. Complete habit")
    click.echo(" 2. Habit overview - manage habits")
    click.echo(" 3. Create new habit")
    click.echo(" 4. Show analytics")
    click.echo(" 5. Save and Exit")
    click.echo(global_menu_block["line"])


def all_habits() -> None:
    """Shows a list of all habits grouped by period"""
    # b auxiliary variable representing menu item list numbers
    # aux_dict for completed habits
    # aux_dict_2 for not completed habits
    b = 1
    habit_list = tracker.Habit.habit_list
    global_dict.clear()
    global_dict_2.clear()
    # habit_list indexes as values, keys=b represent item numbers in list shown to user
    for i in range(len(habit_list)):
        if habit_list[i].period == "daily":
            global_dict_2.update({b: i})
            b += 1
    for i in range(len(habit_list)):
        if habit_list[i].period == "weekly":
            global_dict.update({b: i})
            b += 1
    print_app_heading()
    click.echo(" Habit overview")
    click.echo(global_menu_block["line"])
    click.echo(' 0. Back to main menu')
    click.echo(global_menu_block["daily_line"])
    for i in range(len(global_dict_2)):
        click.echo(f" {i + 1}. {habit_list[global_dict_2[i + 1]].habit_name}")
    click.echo(global_menu_block["weekly_line"])
    for i in range(len(global_dict)):
        aux_i = i + len(global_dict_2) + 1
        click.echo(f" {aux_i}. {habit_list[global_dict[aux_i]].habit_name}")
    click.echo(global_menu_block["line"])


def habit_menu(index) -> None:
    """Menu that shows information on a single habit and 
    gives user options as to view more information and modify the habit

    :param str | int index: index of habit object in habit_list"""

    def calendar_week(date) -> str:
        """Returns calendar week of given date"""
        if isinstance(date, datetime):
            return date.strftime("%V")
        else:
            return "n/a"

    index = int(index)
    habit = tracker.Habit.habit_list[index]
    streak_data = list(analytics_module.habit_streak_stats([habit]).itertuples())[0]
    # initialize auxiliary variables
    if habit.period == "daily":
        auxperiod = "days"
        auxperiod2 = "Daily"
        auxperiod3 = ""
    else:
        auxperiod = "weeks"
        auxperiod2 = "Weekly"
        auxperiod3 = f"- calendar week: {calendar_week(streak_data.streak_c_date)}"
    # print menu habit information
    print_app_heading()
    click.echo(f"---{auxperiod2} habit: {habit.habit_name} ---")
    click.echo(global_menu_block["line"])
    click.echo(f" Created on: {tracker_util.get_date_string(habit.creation_date)}")
    if habit.check_complete_status():
        click.echo(" Completion status: completed!")
    else:
        if habit.period == "daily":
            click.echo(" Completion status: Habit has *not* been completed today!")
        elif habit.period == "weekly":
            click.echo(" Completion status: Habit has *not* been completed this week!")
    if streak_data.streak_c_length > 0:
        click.echo(f" Current streak: {streak_data.streak_c_length} {auxperiod}, started on "
                   f" {tracker_util.get_date_string(streak_data.streak_c_date)} {auxperiod3}")
    else:
        click.echo(" No current streak")
    if streak_data.streak_l_length > 0:
        click.echo(f" Completed periods: {len(habit.complete_time_list)}")
        click.echo(f" Longest streak(s): {streak_data.streak_l_length} {auxperiod}:")
        # print start and end dates
        for i in range(len(streak_data.streak_l_dates)):
            if habit.period == "weekly":
                auxperiod4 = (f" calendar weeks {calendar_week(streak_data.streak_l_dates[i][0])} to "
                              f"{calendar_week(streak_data.streak_l_dates[i][1])}")
            else:
                auxperiod4 = ""
            click.echo(f" from "
                       f"{tracker_util.get_date_string(streak_data.streak_l_dates[i][0])} "
                       f"to {tracker_util.get_date_string(streak_data.streak_l_dates[i][1])}{auxperiod4}")
    else:
        click.echo(" There has not been any completed periods so far")
    click.echo(global_menu_block["line"])
    click.echo(" 0. Return to habit overview")
    click.echo(" 1. View completion dates")
    click.echo(" 2. View completion date statistics")
    click.echo(" 3. Change habit description")
    click.echo(" 4. Change tracking period [daily, weekly] - will reset tracking data")
    click.echo(" 5. Reset tracking data")
    click.echo(" 6. Delete habit")
    click.echo(global_menu_block["line"])


def complete_habit() -> None:
    """Shows a list of all habits grouped by completion status"""
    # b auxiliary variable representing menu item list numbers
    # aux_dict for completed habits
    # aux_dict_2 for not completed habits
    b = 1
    habit_list = tracker.Habit.habit_list
    global_dict.clear()
    global_dict_2.clear()
    # in dictionary: habit_list indexes = values, keys=b represent item numbers in list shown to user
    for i in range(len(habit_list)):
        if not habit_list[i].check_complete_status():
            global_dict_2.update({b: i})
            b += 1
    for i in range(len(habit_list)):
        if habit_list[i].check_complete_status():
            global_dict.update({b: i})
            b += 1
    print_app_heading()
    click.echo(" Which habit have you completed?")
    click.echo(global_menu_block["line"])
    click.echo(" 0. Back to main menu")
    click.echo("------------------Not completed----------------------")
    if len(global_dict_2) == 0 and len(global_dict) == 0:
        click.echo(" -")
    elif len(global_dict_2) == 0:
        click.echo(" All habits have been completed.")
    for i in range(len(global_dict_2)):
        click.echo(
            f" {i + 1}. {habit_list[global_dict_2[i + 1]].habit_name}, {habit_list[global_dict_2[i + 1]].period}")
    click.echo("--------------------Completed------------------------")
    if len(global_dict_2) == 0 and len(global_dict) == 0:
        click.echo(" -")
    elif len(global_dict) == 0:
        click.echo(" Not any habit has been completed.")
    for i in range(len(global_dict)):
        aux_i = i + len(global_dict_2) + 1
        click.echo(f" {aux_i}. {habit_list[global_dict[aux_i]].habit_name}, {habit_list[global_dict[aux_i]].period}")
    click.echo(global_menu_block["line"])


def analytics() -> None:
    """Menu items for analytics menu. User interface gets called separately via app_analytics"""
    date_start = global_variables["date_start"]
    date_end = global_variables["date_end"]
    threshold_daily = global_variables["completion_threshold_daily"]
    potential_daily = tracker_util.day_streak(date_start, date_end)
    threshold_weekly = global_variables["completion_threshold_weekly"]
    potential_weekly = tracker_util.week_streak(date_start, date_end)
    descr = global_variables["descr"]
    custom_period = global_variables["custom_period"]
    var_check_threshold = check_threshold()

    print_app_heading()
    click.echo(" Analytics")
    click.echo(global_menu_block["line"])
    click.echo(" 0. Return to main menu")
    click.echo(global_menu_block["Streaks"])
    click.echo("--------Daily period---------")
    click.echo(" 1. Longest currently")
    click.echo(" 2. Longest all-time")
    click.echo("--------Weekly period--------")
    click.echo(" 3. Longest currently")
    click.echo(" 4. Longest all-time")
    click.echo(global_menu_block["Performance"])
    click.echo(" 5. General overview")
    click.echo("--------Daily period---------")
    click.echo(" 6. Analysis")
    click.echo(" 7. Habit ranking")
    click.echo("--------Weekly period--------")
    click.echo(" 8. Analysis")
    click.echo(" 9. Habit ranking")
    click.echo(global_menu_block["Performance_Settings"])
    click.echo(f" - Chosen period: {descr}{custom_period}")
    click.echo(f" - from {tracker_util.get_date_string(date_start)} until {tracker_util.get_date_string(date_end)}")
    click.echo(
        f" - Min. number of potential completions in period: - daily: {threshold_daily}/{potential_daily} -"
        f" weekly: {threshold_weekly}/{potential_weekly}")
    if var_check_threshold[0] == 0:
        click.echo("Daily threshold exceeds possible completions in period")
    if var_check_threshold[1] == 0:
        click.echo("Weekly threshold exceeds possible completions in period")
    click.echo(global_menu_block["line"])
    click.echo(" 10. Change period")
    click.echo(" 11. Change potential completion threshold ")
    click.echo(" 12. Reset to default")
    click.echo(global_menu_block["line"])


def change_period() -> None:
    print_app_heading()
    click.echo(" Which period should be analysed?")
    click.echo(global_menu_block["line"])
    click.echo(" 0. Return to analysis menu")
    click.echo(" 1. Default values - since earliest creation date of earliest habit")
    click.echo(global_menu_block["Preset_Options"])
    click.echo(" 2. This week*")
    click.echo(" 3. Past 7 days")
    click.echo(" 4. This month*")
    click.echo(" 5. Past 30 days")
    click.echo(" 6. Since beginning of last month")
    click.echo(" 7. Past 12 weeks")
    click.echo(" 8. Since beginning of last quarter")
    click.echo(" 9. This year*")
    click.echo(" 10. Past 365 days")
    click.echo(global_menu_block["Custom_Options"])
    click.echo(" 11. Custom Period (days)")
    click.echo(" 12. Custom Period (weeks)")
    click.echo(" 13. Custom date")
    click.echo(global_menu_block["line"])
    click.echo(" *Including today/this week")
    click.echo(global_menu_block["line"])


def analytics_general_overview() -> None:
    """Displays general performance metrics: number of habits and total and potential completions for
    all, weekly and daily period and corresponding completion rates"""
    all_list = tracker.Habit.habit_list
    df = analytics_module.habit_completion_stats(inlist=all_list,
                                                 indate_start=global_variables["date_start"],
                                                 indate_end=global_variables["date_end"])
    all_habits_count = len(df)
    if len(df) == 0:
        print_app_heading()
        click.echo(" No habit is being tracked")
        click.echo("")
        click.echo(global_menu_block["line"])
        return
    daily_habits_count = len(df.loc[df["period"] == "daily"])
    weekly_habits_count = len(df.loc[df["period"] == "weekly"])
    all_completions = df["act_complet"].sum()
    daily_completions = df.loc[df["period"] == "daily", "act_complet"].sum()
    weekly_completions = df.loc[df["period"] == "weekly", "act_complet"].sum()
    all_p_completions = df["pot_complet_per_credate"].dropna().sum()
    daily_p_completions = df.loc[df["period"] == "daily", "pot_complet_per_credate"].dropna().sum()
    weekly_p_completions = df.loc[df["period"] == "weekly", "pot_complet_per_credate"].dropna().sum()

    print_app_heading()
    click.echo(f" Total number of habits: {all_habits_count} - Completed periods: {all_completions} - "
               f"{int(all_completions / all_p_completions * 100)}% completion rate")
    click.echo(global_menu_block["line"])
    if daily_p_completions == 0:
        click.echo(" No daily habits are being tracked.")
    else:
        click.echo(f" Number of daily habits: {daily_habits_count} - Completed days: {daily_completions} - "
                   f"{int(daily_completions / daily_p_completions * 100)}% completion rate")
    click.echo(global_menu_block["line"])
    if weekly_p_completions == 0:
        click.echo(" No weekly habits are being tracked")
    else:
        click.echo(f" Number of weekly habits: {weekly_habits_count} - Completed weeks: {weekly_completions} - "
                   f"{int(weekly_completions / weekly_p_completions * 100)}% completion rate")
    click.echo(global_menu_block["line"])


def analytics_performance_analysis() -> None:
    """User gets shown statistics on his performance in the chosen period for habits of the chosen period"""
    # daily, weekly
    period = global_variables["period"]
    # start date
    start_date = global_variables["date_start"]
    # end date
    end_date = global_variables["date_end"]
    # daily: this week, past 7 days, this month, past 30 days,
    # this year, past 365 days, custom date, custom period (days)
    # weekly: past 12 weeks, since beginning of last quarter, this year, custom period (weeks), custom date
    # default: since creation date of first tracked habit
    descr = global_variables["descr"]
    # last <number> of <day(s) or week(s)>
    custom_period = global_variables["custom_period"]
    # completion threshold
    if period == "daily":
        threshold = global_variables["completion_threshold_daily"]
    else:  # period == "weekly":
        threshold = global_variables["completion_threshold_weekly"]
    # text variables
    if period == "daily":
        time_since_date = tracker_util.day_streak(start_date, end_date)
        time_text = "days"
        period_upper = "Daily"
    else:  # period == "weekly":
        time_since_date = tracker_util.week_streak(start_date, end_date)
        time_text = "calendar weeks"
        period_upper = "Weekly"

    habit_list = tracker.Habit.habit_list

    if len(habit_list) == 0:
        print_app_heading()
        click.echo(" No habits are being tracked")
        click.echo("")
        return

    df_raw = analytics_module.habit_completion_stats(habit_list, start_date, end_date)
    df_period = df_raw.loc[df_raw['period'] == f'{period}']

    if len(df_period) == 0:
        print_app_heading()
        click.echo(f" No {period} habit is being tracked")
        click.echo("")
        return

    df_threshold_excluded = df_period.loc[(df_period['per_credate_code'] == 3) &
                                          (df_period['pot_complet_credate'] < threshold)]
    df_creation_excluded = df_period.loc[df_period['per_credate_code'] == 0]
    # filtering out excluded habits
    df = df_period.loc[~((df_period['per_credate_code'] == 3) & (df_period['pot_complet_credate'] < threshold)) &
                       ~(df_period['per_credate_code'] == 0)]

    # variables for output
    total_completions = df['act_complet'].sum()
    possible_completions = df['pot_complet_per_credate'].sum()
    if possible_completions == 0:
        completion_rate = 0
    else:
        completion_rate = total_completions / possible_completions * 100
    df_perf_best = analytics_module.performance(df, "best")
    df_perf_worst = analytics_module.performance(df, "worst")
    best_complet_rate = df_perf_best['complet_percent'].max()
    worst_complet_rate = df_perf_worst['complet_percent'].min()
    list_perf_best = list(df_perf_best.itertuples())
    list_perf_worst = list(df_perf_worst.itertuples())
    # print menu items
    print_app_heading()
    click.echo(global_menu_block["Analysis"])
    click.echo(f" {period_upper} performance: [{descr}{custom_period}]")
    click.echo(f" - Period length: {time_since_date} {time_text}"
               f" from {tracker_util.get_date_string((start_date))} until {tracker_util.get_date_string(end_date)}")
    click.echo(global_menu_block["line"])
    if len(df) == 0:
        click.echo(" No completions recorded yet!")
    else:
        click.echo(f" Total completions: {total_completions} out of {possible_completions} possible completions "
                   f"- ({len(df)} {period} habits tracked)")
        click.echo(global_menu_block["line"])
        click.echo(f"-------> Completion rate: {completion_rate}% <-------")
        click.echo(global_menu_block["line"])
        click.echo(f" Best performing habits with {best_complet_rate}% completion rate")
        for i in range(len(list_perf_best)):
            click.echo(f" > {list_perf_best[i].name} with {list_perf_best[i].act_complet}/"
                       f"{list_perf_best[i].pot_complet_per_credate} completions")
        click.echo(global_menu_block["line"])
        click.echo(f" Worst performing habits with {worst_complet_rate}% completion rate")
        for i in range(len(list_perf_worst)):
            click.echo(f" > {list_perf_worst[i].name} with {list_perf_worst[i].act_complet}/"
                       f"{list_perf_worst[i].pot_complet_per_credate} completions")
        click.echo(global_menu_block["line"])
        if len(df_creation_excluded) == 0:
            click.echo(" No habits excluded based on period")
        else:
            click.echo(" Excluded habits due to period:")
            list_creation_excluded = list(df_creation_excluded.itertuples())
            for i in range(len(list_creation_excluded)):
                click.echo(f" - {list_creation_excluded[i].name} - creation date:"
                           f"{tracker_util.get_date_string(list_creation_excluded[i].credate)}")
        if len(df_threshold_excluded) == 0:
            click.echo(f" No habits excluded based on threshold of {threshold}")
        else:
            list_threshold_excluded = list(df_threshold_excluded.itertuples())
            click.echo(f" Excluded habits due to potential completion threshold of {threshold}:")
            for i in range(len(list_threshold_excluded)):
                click.echo(f" - {list_threshold_excluded[i].name} - pot. completions in period: "
                           f"{list_threshold_excluded[i].pot_complet_per_credate}")
    click.echo(global_menu_block["line"])


def analytics_performance_overview() -> None:
    """Shows user ranking of tracked habits in chosen period and of chosen periodicity
    """
    # daily, weekly
    period = global_variables["period"]
    start_date = global_variables["date_start"]
    end_date = global_variables["date_end"]
    # period description
    descr = global_variables["descr"]
    # last <number> of <day(s) or week(s)>
    custom_period = global_variables["custom_period"]
    # completion threshold and text variables
    if period == "daily":
        threshold = global_variables["completion_threshold_daily"]
        time_since_date = tracker_util.day_streak(start_date, end_date)
        time_text = "days"
        period_upper = "Daily"
    else:  # period == "weekly"
        threshold = global_variables["completion_threshold_weekly"]
        time_since_date = tracker_util.week_streak(start_date, end_date)
        time_text = "calendar weeks"
        period_upper = "Weekly"

    habit_list = tracker.Habit.habit_list

    if len(habit_list) == 0:
        print_app_heading()
        click.echo("No habit is being tracked")
        click.echo("")
        return

    df_raw = analytics_module.habit_completion_stats(habit_list, start_date, end_date)
    df_period = df_raw.loc[df_raw['period'] == f'{period}']

    if len(df_period) == 0:
        print_app_heading()
        click.echo(f"No {period} habit is being tracked")
        click.echo("")
        return

    df_threshold_excluded = df_period.loc[(df_period['per_credate_code'] == 3) &
                                          (df_period['pot_complet_credate'] < threshold)]
    df_creation_excluded = df_period.loc[df_period['per_credate_code'] == 0]
    # filtering out excluded habits
    df = df_period.loc[~((df_period['per_credate_code'] == 3) & (df_period['pot_complet_credate'] < threshold)) &
                       ~(df_period['per_credate_code'] == 0)]
    df = df.loc[:, ['name', 'complet_percent', 'act_complet', 'pot_complet_per_credate']]
    df = df.sort_values(by=['complet_percent', 'act_complet'], ascending=False)
    df = df.rename(
        columns={'name': 'habit description', 'act_complet': 'completions',
                 'complet_percent': 'completion rate', 'pot_complet_per_credate': 'potential completions'})
    df['completion rate'] = df['completion rate'].astype(str) + '%'
    df = df.reset_index(drop=True)
    df.index = range(1, len(df) + 1)

    print_app_heading()
    click.echo(global_menu_block["Habit_Ranking"])
    click.echo(f" {period_upper} period: [{descr}{custom_period}]")
    click.echo(f" - Period length: {time_since_date} {time_text}"
               f" from {tracker_util.get_date_string(start_date)} until {tracker_util.get_date_string(end_date)}")
    click.echo(global_menu_block["line"])
    if len(df) == 0:
        click.echo(" No completions recorded yet!")
    else:
        print(df.to_markdown(tablefmt="fancy_grid"))
        click.echo("")
        if len(df_creation_excluded) == 0:
            click.echo(" No habits excluded based on period")
        else:
            click.echo(" Excluded habits due to period:")
            list_creation_excluded = list(df_creation_excluded.itertuples())
            for i in range(len(list_creation_excluded)):
                click.echo(f" - {list_creation_excluded[i].name} - creation date:"
                           f"{tracker_util.get_date_string(list_creation_excluded[i].credate)}")
        if len(df_threshold_excluded) == 0:
            click.echo(f" No habits excluded based on threshold of {threshold}")
        else:
            list_threshold_excluded = list(df_threshold_excluded.itertuples())
            click.echo(f" Excluded habits due to potential completion threshold of {threshold}:")
            for i in range(len(list_threshold_excluded)):
                click.echo(f" - {list_threshold_excluded[i].name} - pot. completions in period: "
                           f"{list_threshold_excluded[i].pot_complet_per_credate}")
    click.echo("")


def choice_date_end() -> None:
    """Menu for date end selection when choosing a custom period in analysis menu"""
    clear_screen()
    print_app_heading()
    click.echo(global_menu_block["line"])
    click.echo(" When should the period end?")
    click.echo(global_menu_block["line"])
    click.echo(" 1. Today")
    click.echo(" 2. Yesterday")
    click.echo(" 3. End of last week")
    click.echo(" 4. Custom date")
    click.echo(global_menu_block["line"])


@click.command()
@click.option('--user_input', prompt=" Enter the number of menu item",
              help='Enter the number of the menu item e.g. enter 4 for Create new habit',
              type=click.Choice(['1', '2', '3', '4', '5'], case_sensitive=False))
def app_main_menu(user_input) -> None:
    """Main menu user interface. Calls submenus oder lets user close the app and save
    :param string user_input: menu item
    """
    # Complete habit
    if user_input == "1":
        clear_screen()
        complete_habit()
        app_complete_habit()
    # manage habits
    elif user_input == "2":
        clear_screen()
        all_habits()
        app_all_habits()
    # create new habit
    elif user_input == "3":
        app_new_habit()
    # show analytics
    elif user_input == "4":
        clear_screen()
        analytics()
        app_analytics()
    # save and exit
    elif user_input == "5":
        try:
            databaseSQL.object_to_db()
            click.echo("Data has been saved successfully")
        except Exception:
            click.echo("Data could not be saved properly due to an error.")


@click.command()
@click.option('--habit_name', prompt=" Which habit do you like to track?",
              help='Enter the number of the menu item e.g. enter 4 for Create new habit')
@click.option('--period', prompt=" Should the habit be tracked \'daily\' or \'weekly\'?",
              type=click.Choice(['daily', 'weekly'], case_sensitive=True))
def app_new_habit(habit_name, period) -> None:
    """User interface for creating a new habit. User enters habit name and period.
    :param string habit_name: user input for habit name
    :param string period: user input for periodicity
    """
    # creates new habit object based on user input. New habit object will be automatically added to class list
    # habit_list
    try:
        tracker.Habit(habit_name, period)
        click.echo(global_menu_block["line"])
        click.echo("--- Entry successful ---")
        click.echo(global_menu_block["line"])
        click.echo(f"--- {habit_name} will now be tracked on a {period} basis ---")
        click.echo(global_menu_block["line"])
    except Exception:
        main_menu()
        click.echo(global_menu_block["line"])
        click.echo("--- An error occurred. Could not save new habit. ---")
        click.echo(global_menu_block["line"])
    app_main_menu()


@click.command()
@click.option('--user_input', prompt=' Please enter habit number or 0 to return to main menu', type=int)
def app_all_habits(user_input) -> None:
    """User interface for all_habits menu. User picks which habit to manage and view more information on
    based on menu item list numbers or 0 to return to main menu.
    :param int user_input: menu item"""
    # key for aux_dictionaries
    key = int(user_input)
    # merge auxiliary dictionaries
    global_dict.update(global_dict_2)
    # return to main menu
    if int(user_input) == 0:
        clear_screen()
        main_menu()
        app_main_menu()
    elif key in global_dict:
        index = global_dict.get(key)
        clear_screen()
        habit_menu(index)
        app_habit_menu(f"{index}")
    else:
        click.echo(" Error. Invalid input. Please enter a number of a habit in the list.")
        app_all_habits()


@click.command()
@click.option('--user_input', prompt=' Input number of option or 0 to go back to habit overview',
              type=click.Choice(["0", "1", "2", "3", "4", "5", "6"]))
@click.argument("index")
# index variable corresponds to index in habit_list
def app_habit_menu(user_input, index) -> None:
    """User interface for habit_menu. User selects option
    :param string user_input: menu item
    :param string | int index: index of habit object in habit_list"""
    # go back to previous menu
    habit = tracker.Habit.habit_list[int(index)]
    if user_input == "0":
        clear_screen()
        all_habits()
        app_all_habits()
    # print all completion dates
    elif user_input == "1":
        clear_screen()
        print_app_heading()
        click.echo("-------Completion dates-------")
        click.echo(global_menu_block["line"])
        if habit.complete_time_list:
            for i in range(len(habit.complete_time_list)):
                click.echo(f"{i + 1}. "
                           f"{tracker_util.get_date_string(habit.complete_time_list[i])}")
                click.echo(global_menu_block["line"])
        else:
            click.echo(" Habit has not been completed on any day yet!")
            click.echo(global_menu_block["line"])
        app_back_to_habit_menu(index)
    # completion date stats
    elif user_input == "2":
        clear_screen()
        print_app_heading()
        click.echo("---------Completions by month---------")
        if not habit.complete_time_list:
            click.echo(" No completions yet!")
            click.echo("")
        else:
            cdates = analytics_module.count_completion_dates_statistics(habit)
            credate_year = habit.creation_date.year
            credate_month = habit.creation_date.month
            today_year = datetime.today().year
            today_month = datetime.today().month
            for y in range(len(cdates)):
                year = today_year - y
                click.echo(f" Year {year}")
                click.echo("---------------")
                for m in range(12, 0, -1):
                    if (credate_year == year and m < credate_month) or (today_year == year and today_month < m):
                        continue
                    else:
                        click.echo(f" - {calendar.month_name[m]}: {cdates[y][m-1]}")
                click.echo(global_menu_block["line"])
        app_back_to_habit_menu(index)
    # change habit description
    elif user_input == "3":
        app_change_habit_name(index)
    # change period
    elif user_input == "4":
        app_change_habit_period(index)
    # clear tracking data
    elif user_input == "5":
        habit.clear_tracking_data()
        click.echo(global_menu_block["line"])
        click.echo(" Tracking data has been reset.")
        click.echo(global_menu_block["line"])
        app_back_to_habit_menu(index)
    # delete habit from habit_list
    elif user_input == "6":
        _ = tracker.Habit.habit_list.pop(int(index))
        clear_screen()
        main_menu()
        click.echo(global_menu_block["line"])
        click.echo(" Habit has been deleted.")
        click.echo(global_menu_block["line"])
        app_main_menu()


@click.command()
@click.option('--user_input', prompt=' Please input new habit description')
@click.argument("index")
def app_change_habit_name(index, user_input) -> None:
    """User interface: user enters new habit name

    :param string index: list index of habit in habit_list
    :param string user_input: habit name"""
    tracker.Habit.habit_list[int(index)].habit_name = user_input
    clear_screen()
    habit_menu(index)
    click.echo(global_menu_block["line"])
    click.echo(f" New habit name {user_input} has been saved.")
    click.echo(global_menu_block["line"])
    app_habit_menu(index)


@click.command()
@click.option('--user_input', prompt=' Please input new habit period:',
              type=click.Choice(['daily', 'weekly'], case_sensitive=False))
@click.argument("index")
def app_change_habit_period(index, user_input) -> None:
    """User interface: user enters tracking period

    :param string index: list index of habit in habit_list
    :param string user_input: habit periodicity"""
    habit = tracker.Habit.habit_list[int(index)]
    # if user_input is different from period attribute, user data gets wiped
    if habit.period == user_input:
        click.echo(global_menu_block["line"])
        click.echo(f" Current tracking period was already {user_input}.")
        click.echo(global_menu_block["line"])
    else:
        habit.clear_tracking_data()
        habit.period = user_input
        click.echo(global_menu_block["line"])
        click.echo(f" New habit period {user_input} has been saved.")
        click.echo(global_menu_block["line"])
        click.echo(" Old tracking data has been deleted as tracking period has been changed.")
        click.echo(global_menu_block["line"])
    app_back_to_habit_menu(index)


@click.command()
@click.option('--user_input', prompt=' Please enter habit number or 0 to return to main menu', type=int)
def app_complete_habit(user_input) -> None:
    """User interface for complete_habit menu. User picks which habit to complete based on menu item list numbers
    or 0 to return to main menu.
    :param int user_input: menu item"""
    # key for aux_dictionaries
    key = int(user_input)
    # merge auxiliary dictionaries
    global_dict.update(global_dict_2)
    # return to main menu
    if int(user_input) == 0:
        clear_screen()
        main_menu()
        app_main_menu()
    elif key in global_dict:
        habit = tracker.Habit.habit_list[global_dict[key]]
        check_complete = habit.check_complete_status()
        # if check_complete is True, then habit has already been completed in current period
        if check_complete:
            click.echo(global_menu_block["line"])
            click.echo(
                f' Habit \"{habit.habit_name}\" has already been completed in current period')
            click.echo(global_menu_block["line"])
            app_complete_habit()
        # if check_complete is False, then habit has not been completed in current period
        else:
            habit.complete_habit()
            click.echo(global_menu_block["line"])
            click.echo(
                f' Habit \"{habit.habit_name}\" has been completed on '
                f'{tracker_util.get_date_string(habit.complete_time_list[-1])}')
            click.echo(global_menu_block["line"])
            varstreak = analytics_module.streak_current(habit.complete_time_list, habit.period)[0]
            if varstreak > 1:
                click.echo(
                    f' Congratulations. You are currently on a {varstreak} periods '
                    f'{habit.period} streak!')
                click.echo(global_menu_block["line"])
            else:
                click.echo(' You started a new streak!')
                click.echo(global_menu_block["line"])
            app_back_to_main_menu()
    else:
        click.echo(" Error. Invalid input. Please enter the number of a habit in the list.")
        app_complete_habit()


@click.command()
@click.option('--user_input', prompt=' Please enter number of option',
              type=click.Choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]))
def app_analytics(user_input) -> None:
    """User interface for analytics/statistics of all habits. User selects menu option and corresponding information
    gets displayed to the user
    :param string user_input: menu item number"""
    habit_list = tracker.Habit.habit_list
    # longest current streaks
    if user_input == "1":
        period_list = tracker_util.filter_habit_list(habit_list, "daily")
        clear_screen()
        print_app_heading()
        if period_list:
            df = analytics_module.habit_streak_stats(period_list)
            current_streak = list(analytics_module.streak_data(df, "current").itertuples())
            if current_streak[0].streak_c_length == 0:
                click.echo(global_menu_block["line"])
                click.echo(" No daily habit is currently on a streak")
                click.echo(global_menu_block["line"])
            else:
                click.echo(global_menu_block["line"])
                click.echo(" Longest daily streak(s) currently:")
                for i in range(len(current_streak)):
                    click.echo(global_menu_block["line"])
                    click.echo(
                        f" {current_streak[i].name} with {current_streak[i].streak_c_length} days")
                    click.echo(
                        f" Streak started at "
                        f" {tracker_util.get_date_string(current_streak[i].streak_c_date)}")
                click.echo(global_menu_block["line"])
        else:
            click.echo(global_menu_block["line"])
            click.echo(" No daily habit has been being tracked")
            click.echo(global_menu_block["line"])
        app_back_to_analytics()
    # Longest daily streak(s)
    elif user_input == "2":
        period_list = tracker_util.filter_habit_list(habit_list, "daily")
        clear_screen()
        print_app_heading()
        if period_list:
            df = analytics_module.habit_streak_stats(period_list)
            streak_longest = list(analytics_module.streak_data(df, "longest").itertuples())
            if streak_longest[0].streak_l_length == 0:
                click.echo(global_menu_block["line"])
                click.echo(" No daily habit has been completed")
                click.echo(global_menu_block["line"])
            else:
                if len(streak_longest) > 1:
                    text = "s"
                else:
                    text = ""
                click.echo(global_menu_block["line"])
                click.echo(f" Longest daily streak{text} ever:")
                # loop that prints name and respective streak information for each habit
                for i in range(len(streak_longest)):
                    # loop over list of streak dates
                    for b in range(len(streak_longest[i].streak_l_dates)):
                        click.echo(global_menu_block["line"])
                        click.echo(
                            f" {streak_longest[i].name} with {streak_longest[i].streak_l_length} days")
                        click.echo(
                            f" Streak went from "
                            f"{tracker_util.get_date_string(streak_longest[i].streak_l_dates[b][0])} to "
                            f"{tracker_util.get_date_string(streak_longest[i].streak_l_dates[b][1])}")
                click.echo(global_menu_block["line"])
        else:
            click.echo(global_menu_block["line"])
            click.echo(" No daily habit has been being tracked")
            click.echo(global_menu_block["line"])
        app_back_to_analytics()
    # displays longest current weekly streaks
    elif user_input == "3":
        period_list = tracker_util.filter_habit_list(habit_list, "weekly")
        clear_screen()
        print_app_heading()
        if period_list:
            df = analytics_module.habit_streak_stats(period_list)
            current_streak = list(analytics_module.streak_data(df, "current").itertuples())
            if current_streak[0].streak_c_length == 0:
                click.echo(global_menu_block["line"])
                click.echo(" No weekly habit is currently on a streak")
                click.echo(global_menu_block["line"])
            else:
                click.echo(global_menu_block["line"])
                if len(current_streak) == 1:
                    text = ""
                else:
                    text = "s"
                click.echo(f" Longest weekly streak{text} currently:")
                # loop that prints name and respective streak
                for i in range(len(current_streak)):
                    click.echo(global_menu_block["line"])
                    click.echo(
                        f" {current_streak[i].name} with {current_streak[i].streak_c_length} days")
                    click.echo(
                        f" Streak started at "
                        f"{tracker_util.get_date_string(current_streak[i].streak_c_date)}")
        else:
            click.echo(global_menu_block["line"])
            click.echo(" No weekly habit has been being tracked")
            click.echo(global_menu_block["line"])
        app_back_to_analytics()
    # displays longest all-time weekly streaks
    elif user_input == "4":
        period_list = tracker_util.filter_habit_list(habit_list, "weekly")
        clear_screen()
        print_app_heading()
        if period_list:
            df = analytics_module.habit_streak_stats(period_list)
            streak_longest = list(analytics_module.streak_data(df, "longest").itertuples())
            if streak_longest[0].streak_l_length == 0:
                click.echo(global_menu_block["line"])
                click.echo(" No weekly habit has been completed")
                click.echo(global_menu_block["line"])
            else:
                if len(streak_longest) > 1:
                    text = "s"
                else:
                    text = ""
                click.echo(global_menu_block["line"])
                click.echo(f" Longest weekly streak{text} ever:")
                # loop that prints name and respective streak information for each habit
                for i in range(len(streak_longest)):
                    # loop over list of streak dates
                    for b in range(len(streak_longest[i].streak_l_dates)):
                        click.echo(global_menu_block["line"])
                        click.echo(
                            f" {streak_longest[i].name} with {streak_longest[i].streak_l_length} days")
                        click.echo(
                            f" Streak went from "
                            f"{tracker_util.get_date_string(streak_longest[i].streak_l_dates[b][0])} to "
                            f"{tracker_util.get_date_string(streak_longest[i].streak_l_dates[b][1])}")
                click.echo(global_menu_block["line"])
        else:
            click.echo(global_menu_block["line"])
            click.echo(" No weekly habit has been being tracked")
            click.echo(global_menu_block["line"])
        app_back_to_analytics()
    # General overview performance
    if user_input == "5":
        clear_screen()
        analytics_general_overview()
        app_back_to_analytics()
    # Daily performance analysis
    elif user_input == "6":
        global_variables["period"] = "daily"
        clear_screen()
        analytics_performance_analysis()
        app_back_to_analytics()
    # Daily performance overview
    elif user_input == "7":
        global_variables["period"] = "daily"
        clear_screen()
        analytics_performance_overview()
        app_back_to_analytics()
    # Weekly performance analysis
    elif user_input == "8":
        global_variables["period"] = "weekly"
        clear_screen()
        analytics_performance_analysis()
        app_back_to_analytics()
    # Weekly performance overview
    elif user_input == "9":
        global_variables["period"] = "weekly"
        clear_screen()
        analytics_performance_overview()
        app_back_to_analytics()
    # change period
    elif user_input == "10":
        clear_screen()
        change_period()
        app_change_period()
    # change potential completion threshold
    elif user_input == "11":
        app_set_threshold()
    # reset global variables
    elif user_input == "12":
        reset_global_variables()
        clear_screen()
        analytics()
        click.echo(" Metrics have been reset to default values.")
        app_analytics()
    # return to main menu
    elif user_input == "0":
        clear_screen()
        main_menu()
        app_main_menu()


@click.command()
@click.option('--user_input', prompt=" Please enter option number",
              type=click.Choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]))
def app_change_period(user_input) -> None:
    """User interface: user picks option and changes global values -> period start and end date
    :param string user_input: item number of change_period menu
    """
    if user_input == "0":
        clear_screen()
        analytics()
        app_analytics()
    # default values
    elif user_input == "1":
        reset_global_variables()
        clear_screen()
        analytics()
        app_analytics()
    # this week
    elif user_input == "2":
        global_variables["custom_period"] = ""
        week_day = datetime.today().isoweekday()
        cutoff_date = datetime.today() - timedelta(days=week_day - 1)
        end_date = datetime.today()
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["this_week"]
        clear_screen()
        analytics()
        app_analytics()
    # past 7 days
    elif user_input == "3":
        global_variables["custom_period"] = ""
        cutoff_date = datetime.today() - timedelta(days=7)
        end_date = datetime.today() - timedelta(days=1)
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["past_7_days"]
        clear_screen()
        analytics()
        app_analytics()
    # this month
    elif user_input == "4":
        global_variables["custom_period"] = ""
        month_day = datetime.today().day
        cutoff_date = datetime.today() - timedelta(days=month_day - 1)
        end_date = datetime.today()
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["this_month"]
        clear_screen()
        analytics()
        app_analytics()
    # past 30 days
    elif user_input == "5":
        global_variables["custom_period"] = ""
        cutoff_date = datetime.today() - timedelta(days=30)
        end_date = datetime.today() - timedelta(days=1)
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["past_30_days"]
        clear_screen()
        analytics()
        app_analytics()
    # since beginning of last month
    elif user_input == "6":
        global_variables["custom_period"] = ""
        month = datetime.today().month - 1
        year = datetime.today().year
        if month == 0:
            month = 12
            year = year - 1
        cutoff_date = datetime(year, month, 1)
        end_date = datetime.today()
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["beginning_last_month"]
        clear_screen()
        analytics()
        app_analytics()
    # past 12 weeks
    elif user_input == "7":
        global_variables["custom_period"] = ""
        week_day = datetime.today().isoweekday()
        cutoff_date = datetime.today() - timedelta(days=week_day - 1) - timedelta(weeks=12)
        end_date = datetime.today() - timedelta(days=week_day)
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["past_12_weeks"]
        clear_screen()
        analytics()
        app_analytics()
    # since beginning of last quarter
    elif user_input == "8":
        global_variables["custom_period"] = ""
        if datetime.today().month in (1, 2, 3):
            cutoff_date = datetime((datetime.today().year - 1), 10, 1)
        elif datetime.today().month in (4, 5, 6):
            cutoff_date = (datetime.today().year, 1, 1)
        elif datetime.today().month in (7, 8, 9):
            cutoff_date = (datetime.today().year, 4, 1)
        else: #  datetime.today().month in (10, 11, 12)
            cutoff_date = (datetime.today().year, 7, 1)
        end_date = datetime.today()
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["beginning_last_quarter"]
        clear_screen()
        analytics()
        app_analytics()
    # this year
    elif user_input == "9":
        global_variables["custom_period"] = ""
        cutoff_date = datetime(datetime.today().year, 1, 1)
        end_date = datetime.today()
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["this_year"]
        clear_screen()
        analytics()
        app_analytics()
    # past 365 days
    elif user_input == "10":
        global_variables["custom_period"] = ""
        cutoff_date = datetime.today() - timedelta(days=365)
        end_date = datetime.today() - timedelta(days=1)
        global_variables["date_start"] = cutoff_date
        global_variables["date_end"] = end_date
        global_variables["descr"] = global_period_options["past_365_days"]
        clear_screen()
        analytics()
        app_analytics()
    # custom period (days)
    elif user_input == "11":
        global_variables["custom_period"] = ""
        global_variables["descr"] = global_period_options["custom_period_days"]
        app_custom_period_daily()
    # custom period (weeks)
    elif user_input == "12":
        global_variables["custom_period"] = ""
        global_variables["descr"] = global_period_options["custom_period_weeks"]
        app_custom_period_weekly()
    # custom date
    elif user_input == "13":
        global_variables["custom_period"] = ""
        global_variables["descr"] = global_period_options["custom_date"]
        app_custom_date_start()


@click.command()
@click.option('--user_year', prompt=" Please enter year of period start")
@click.option('--user_month', prompt=" Please enter month of period start",
              type=click.Choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]))
@click.option('--user_day', prompt=" Please enter day of period start")
def app_custom_date_start(user_year, user_month, user_day) -> None:
    """User chooses custom date start by entering year, month and day

    :type user_year: string
    :type user_month: string
    :type user_day: string
    """
    int_day = int(user_day)
    int_month = int(user_month)
    int_year = int(user_year)
    # input check for number of days of month
    if int_day == 29 and not calendar.isleap(int_year) and int_month == 2:
        click.echo(f" Invalid input: {int_year} is not a leap year. February only has 28 days")
        app_custom_date_start()
    elif int_day > 29 and int_month == 2:
        if calendar.isleap(int_year):
            click.echo(f" Invalid input: February only has 29 days in {int_year} as it is a leap year")
            app_custom_date_start()
        else:
            click.echo(f" Invalid input: February only has 28 days")
            app_custom_date_start()
    elif int_day == 31 and int_month in [4, 6, 7, 9, 11]:
        click.echo(f" Invalid input: {calendar.month_name[int_month]} only has 30 days")
        app_custom_date_start()
    else:
        global_variables["date_start"] = datetime(int_year, int_month, int_day)
        choice_date_end()
        app_choice_date_end()


@click.command()
@click.option('--user_choice', prompt=" Please enter option",
              type=click.Choice(["1", "2", "3", "4"]))
def app_choice_date_end(user_choice) -> None:
    """User interface: user chooses premade options for period end date or custom option"""
    # today
    if user_choice == "1":
        global_variables["date_end"] = datetime.today()
        analytics()
        app_analytics()
        # yesterday
    elif user_choice == "2":
        date_end = datetime.today() - timedelta(days=1)
        if date_end < global_variables["date_start"]:
            click.echo(" Invalid input: end date cannot be yesterday if period starts today.")
            app_choice_date_end()
        else:
            global_variables["date_end"] = date_end
            analytics()
            app_analytics()
    # end of last week
    elif user_choice == "3":
        date_end = datetime.today() - timedelta(days=(datetime.today().isoweekday()))
        if date_end < global_variables["date_start"]:
            click.echo(" Invalid input: end date cannot be end of last week if period starts this week.")
            app_choice_date_end()
        else:
            global_variables["date_end"] = date_end
            clear_screen()
            analytics()
            app_analytics()
    elif user_choice == "4":
        app_custom_date_end()


@click.command()
@click.option('--user_year', prompt=" Please enter year of period end")
@click.option('--user_month', prompt=" Please enter month of period end",
              type=click.Choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]))
@click.option('--user_day', prompt=" Please enter day of period end")
def app_custom_date_end(user_year, user_month, user_day) -> None:
    """User chooses custom date end by entering year, month and day

    :type user_year: string
    :type user_month: string
    :type user_day: string
    """
    int_day = int(user_day)
    int_month = int(user_month)
    int_year = int(user_year)

    # input check for number of days of month
    if int_day == 29 and not calendar.isleap(int_year) and int_month == 2:
        click.echo(f" Invalid input: {int_year} is not a leap year. February only has 28 days")
        app_custom_date_end()
    elif int_day > 29 and int_month == 2:
        if calendar.isleap(int_year):
            click.echo(f" Invalid input: February only has 29 days in {int_year} as it is a leap year")
            app_custom_date_end()
        else:
            click.echo(f" Invalid input: February only has 28 days")
            app_custom_date_end()
    elif int_day == 31 and int_month in [4, 6, 7, 9, 11]:
        click.echo(f" Invalid input: {calendar.month_name[int_month]} only has 30 days")
        app_custom_date_end()
    else:
        date_end = datetime(int_year, int_month, int_day)
        if date_end < global_variables["date_start"]:
            text_date = tracker_util.get_date_string(global_variables["date_start"])
            click.echo(f" Invalid input: end date is before the start date: "
                       f"{text_date}")
            app_custom_date_end()
        else:
            global_variables["date_end"] = datetime(int_year, int_month, int_day)
            clear_screen()
            analytics()
            app_analytics()


@click.command()
@click.option('--user_number', prompt=" Please enter number of days", type=int)
def app_custom_period_daily(user_number) -> None:
    """User enters custom period e.g. 23 days

    :type user_number: int"""

    if user_number < 1:
        click.echo(" Invalid input. Number of days cannot be zero or negative")
        app_custom_period_daily()

    if user_number > 1:
        plural_s = "s"
    else:
        plural_s = ""

    global_variables["custom_period"] = f": last {user_number} day{plural_s}"
    choice_date_end()
    app_period_choice_date_end()


@click.command()
@click.option('--user_number', prompt="Please enter number of weeks", type=int)
def app_custom_period_weekly(user_number) -> None:
    """User enters custom period e.g. 23 days

    :type user_number: int"""

    if user_number < 1:
        click.echo(" Invalid input. Number of weeks cannot be zero or negative")
        app_custom_period_weekly()
    else:
        if user_number > 1:
            plural_s = "s"
        else:
            plural_s = ""

        global_variables["custom_period"] = f": last {user_number} week{plural_s}"
        global_variables["period"] = "weekly"
        global_variables["period_number"] = user_number
        choice_date_end()
        app_period_choice_date_end()


@click.command()
@click.option('--user_choice', prompt=" Please enter option",
              type=click.Choice(["1", "2", "3", "4"]))
def app_period_choice_date_end(user_choice) -> None:
    """User interface: user pick either premade option for end date of period or picks custom option. Start date gets
    calculated and saved
    :param string user_choice: """
    if global_variables["period"] == "daily":
        period_factor = 1
    else:  # global_variables["period"] == "weekly"
        period_factor = 7
    # today
    if user_choice == "1":
        date_end = datetime.today()
        global_variables["date_end"] = date_end
        global_variables["date_start"] = date_end - timedelta(days=(period_factor * global_variables["period_number"]))
        clear_screen()
        analytics()
        app_analytics()
    # yesterday
    elif user_choice == "2":
        date_end = datetime.today() - timedelta(days=1)
        global_variables["date_end"] = date_end
        global_variables["date_start"] = date_end - timedelta(days=(period_factor * global_variables["period_number"]))
        clear_screen()
        analytics()
        app_analytics()
    # end of last week
    elif user_choice == "3":
        date_end = datetime.today() - timedelta(days=datetime.today().isoweekday())
        global_variables["date_end"] = date_end
        # -1 to jump to Monday of next week
        global_variables["date_start"] = (date_end -
                                          timedelta(days=(period_factor * global_variables["period_number"] - 1)))
        clear_screen()
        analytics()
        app_analytics()
    elif user_choice == "4":
        app_custom_period_date_end()


@click.command()
@click.option('--user_year', prompt=" Please enter year")
@click.option('--user_month', prompt=" Please enter month",
              type=click.Choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]))
@click.option('--user_day', prompt=" Please enter day")
def app_custom_period_date_end(user_day, user_month, user_year) -> None:
    """User interface: user enters custom end date for custom period
    :type user_year: string
    :type user_month: string
    :type user_day: string
    """
    int_day = int(user_day)
    int_month = int(user_month)
    int_year = int(user_year)
    # input check for number of days of month
    if int_day == 29 and not calendar.isleap(int_year) and int_month == 2:
        click.echo(f" Invalid input: {int_year} is not a leap year. February only has 28 days")
        app_custom_period_date_end()
    elif int_day > 29 and int_month == 2:
        if calendar.isleap(int_year):
            click.echo(f" Invalid input: February only has 29 days in {int_year} as it is a leap year")
            app_custom_period_date_end()
        else:
            click.echo(f" Invalid input: February only has 28 days")
            app_custom_period_date_end()
    elif int_day == 31 and int_month in [4, 6, 7, 9, 11]:
        click.echo(f" Invalid input: {calendar.month_name[int_month]} only has 30 days")
        app_custom_period_date_end()
    else:
        global_variables["date_end"] = datetime(int_year, int_month, int_day)
        if global_variables["period"] == "daily":
            period_factor = 1
        else:  # global_variables["period"] == "weekly"
            period_factor = 7
        global_variables["date_start"] = (global_variables["date_end"] -
                                          timedelta(days=period_factor * global_variables["period_number"]))
        clear_screen()
        analytics()
        app_analytics()


@click.command()
@click.option('--period', prompt=" For which period do you like to change the threshold?",
              type=click.Choice(["daily", "weekly"]))
@click.option('--user_number',
              prompt=" Please enter potential completion threshold (0 -> shows all habits)", type=int)
def app_set_threshold(period, user_number) -> None:
    """User enters custom potential completion threshold for analysis"""
    user_input = int(user_number)
    if user_input < 0:
        click.echo(" Invalid input. Please enter a non-negative number.")
        app_set_threshold()
    else:
        if period == "daily":
            global_variables["completion_threshold_daily"] = user_input
        elif period == "weekly":
            global_variables["completion_threshold_weekly"] = user_input
        clear_screen()
        analytics()
        app_analytics()


@click.command()
@click.option('--user_input', prompt=" Please enter anything to go back to main menu")
def app_back_to_main_menu(user_input) -> None:
    """Prompt to return to main menu
    :type user_input: string"""
    clear_screen()
    main_menu()
    app_main_menu()


@click.command()
@click.option('--user_input', prompt=" Please enter anything to go back to analytics")
def app_back_to_analytics(user_input) -> None:
    """Prompt to return to analytics menu
    :type user_input: string"""
    clear_screen()
    analytics()
    app_analytics()


@click.command()
@click.option('--user_input', prompt=" Please enter anything to go back to habit menu")
@click.argument("index")
def app_back_to_habit_menu(user_input, index) -> None:
    """Prompt to return to respective habit menu.

    :type user_input: string
    :param int index: list index of habit object in habit_list
    :type index: int
    :return: None"""
    clear_screen()
    habit_menu(index)
    app_habit_menu(index)


def reset_global_variables() -> None:
    """Resets global variables to default values"""
    if len(tracker.Habit.habit_list) == 0:
        global_variables['date_start'] = datetime.today()
    else:
        global_variables["date_start"] = tracker_util.get_earliest_creation_date(tracker.Habit.habit_list)
    global_variables["period"] = "None"
    global_variables["period_number"] = 0
    global_variables["date_end"] = datetime.today()
    global_variables["descr"] = global_period_options["default"]
    global_variables["custom_period"] = ""
    global_variables["completion_threshold_daily"] = 30
    global_variables["completion_threshold_weekly"] = 10


def clear_screen() -> None:
    """Clears command line interface"""
    if os.name == 'nt':  # for windows
        _ = os.system('cls')
    else:  # for mac and linux
        _ = os.system('clear')


def check_threshold() -> tuple:
    """Checks if potential completion threshold exceeds possible completions in period
    :returns: tuple[int, int]: check for [daily, weekly] 0 = check unsuccessful
    """
    if (tracker_util.day_streak(global_variables["date_start"], global_variables["date_end"]) <
            global_variables["completion_threshold_daily"]):
        daily = 0
    else:
        daily = 1

    if (tracker_util.week_streak(global_variables["date_start"], global_variables["date_end"]) <
            global_variables["completion_threshold_weekly"]):
        weekly = 0
    else:
        weekly = 1

    return daily, weekly


def print_app_heading():
    click.echo("-----------------------------------------------------")
    click.echo("------------------Habit Tracker App------------------")
    click.echo("")


def main():
    # loads database into memory
    databaseSQL.app_load_data_base()
    # sorts habit list alphabetically
    tracker.Habit.habit_list.sort(key=lambda x: x.habit_name)
    # calls menu and user interface
    reset_global_variables()
    clear_screen()
    main_menu()
    app_main_menu()


if __name__ == "__main__":
    main()
