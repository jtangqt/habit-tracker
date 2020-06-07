from datetime import datetime, timedelta, time, date
import pytz

from enum_helper import XEnum
from postgres import with_postgres_connection
from json_record import JSONRecord


class DaysOfTheWeek(str, XEnum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'


class MonthsOfTheYear(str, XEnum):
    JANUARY = 'January'
    FEBRUARY = 'February'
    MARCH = 'March'
    APRIL = 'April'
    MAY = 'May'
    JUNE = 'June'
    JULY = 'July'
    AUGUST = 'August'
    SEPTEMBER = 'September'
    OCTOBER = 'October'
    NOVEMBER = 'November'
    DECEMBER = 'December'


class Goals2020(str, XEnum):
    JOBS = "Get a job by August"
    WEIGHT = "Get to 51kg by September"
    BLOG = "Write at least one article a week in December"


class Weekly(JSONRecord):
    def __init__(self, number=None, days_of_the_week=None):
        self.weekly_cadence = {
            "number": number,
            "days_of_the_week": days_of_the_week
        }
        super().__init__(self.weekly_cadence)
    # todo


class Monthly(JSONRecord):
    def __init__(self, number=None, days_of_the_month=None):
        self.monthly_cadence = {
            "number": number,
            "days_of_the_month": days_of_the_month
        }
        super().__init__(self.monthly_cadence)
    # todo


class Yearly(JSONRecord):
    def __init__(self, number=None, dates=None):
        self.yearly_cadence = {
            "number": number,
            "dates": dates
        }
        super().__init__(self.yearly_cadence)
    # todo


class Task:
    def __init__(self):
        self.idx = None
        self.task_name = None
        self.created_on = None
        self.start_date = None
        self.end_date = None
        self.due_date = None
        self.once = False
        self.yearly = Yearly
        self.monthly = Monthly
        self.weekly = Weekly()
        self.daily = False
        self.is_complete = {}
        self.task_dependencies = {}
        self.project = ""
        self.subproject = ""
        self.goal = Goals2020
        self.habit = False
        self.related_tasks = {}  # this is for future use
        # determine how long it takes to complete related projects/tasks on average
        # to generate estimate for current project/task
        # self.time_spent = {date: timedelta} # this tracks how long I've spent on this task(s)

    def unpack_records(self, record):
        # questions: how do you enforce one element is one of those types
        for i, key in enumerate(self.__dict__):
            self.__dict__[key] = record[i]
    def update(self, task):
        #todo
        return None


@with_postgres_connection
def insert_row(cursor, task_name, operation_name="inserted", table_name="todo_list"):
    insert_entry = 'insert into todo_list (task_name) values (%s)'
    cursor.execute(insert_entry, (task_name,))
    return None


@with_postgres_connection
def find_task_entries_for_task_name(cursor, task_name, operation_name="found (all)", table_name="todo_list"):
    try:
        query = 'select * from todo_list where task_name = %s'
        cursor.execute(query, (task_name,))
        records = cursor.fetchall()
        if records is None:
            raise Exception("Error: record for task {} does not exist".format(task_name))
    except (Exception, psycopg2.Error) as error:
        return None, error
    return records, None


@with_postgres_connection
def find_task_entry_for_task_id(cursor, idx, operation_name="found", table_name="todo_list"):
    try:
        query = 'select * from todo_list where idx = %s'
        cursor.execute(query, (idx,))
        record = cursor.fetchone()
        if record is None:
            raise Exception("Error: record for task {} does not exist".format(task_name))
    except (Exception, psycopg2.Error) as error:
        return None, error
    return record, None


@with_postgres_connection
def update_task_entry_for_task_id(cursor, idx, entries: Task, operation_name="updated",
                                  table_name="todo_list"):
    update_entry = 'update todo_list ' \
                   'set task_name = %s, created_on = %s, start_date = %s, end_date = %s, due_date = %s, ' \
                   'occurence_once = %s, occurence_yearly = %s, occurence_monthly = %s, occurence_weekly = %s, occurence_daily = %s, ' \
                   'is_complete = %s, task_dependencies = %s, project = %s, subproject = %s, ' \
                   'goal = %s, habit = %s, related_tasks = %s ' \
                   'where idx = %s'
    data = (
        entries.task_name, entries.created_on, entries.start_date, entries.end_date, entries.due_date,
        entries.once, entries.yearly, entries.monthly, entries.weekly, entries.daily,
        entries.is_complete, entries.task_dependencies, entries.project, entries.subproject,
        entries.goal, entries.habit, entries.related_tasks,
        idx)
    cursor.execute(update_entry, data)


@with_postgres_connection
def delete_task_entry_for_task_id(cursor, idx, operation_name="deleted", table_name="todo_list"):
    query = 'delete from todo_list where idx = %s'
    cursor.execute(query, (idx,))


@with_postgres_connection
def delete_all_task_entries_for_task_name(cursor, task_name, operation_name="deleted", table_name="todo_list"):
    query = 'delete from todo_list where task_name = %s'
    cursor.execute(query, (task_name,))


def insert_task(task_name):
    return insert_row(task_name)


def get_task_entries(task_name):
    records, err = find_task_entries_for_task_name(task_name)
    if err is not None:
        return None, err
    print("Info: got {} record successfully".format(len(records)))
    return records, None

def get_task_entry_by_idx(idx):
    record, err = find_task_entry_for_task_id(idx)
    if err is not None:
        return None, err
    task_entry = Task()
    task_entry.unpack_records(record)
    print("Info: got 1 record successfully")
    return task_entry, None


def update_task_entry(task_name, task: Task):
    records, err = find_task_entries_for_task_name(task_name)
    if err is not None:
        return err
    indexes = {}
    items = "Please indicate which index you'd like to update\n"
    for record in records:
        indexes[str(record[0])] = 0
        items += "{}: {}\n".format(record[0], record[1:])
    ans = input(
        items
    )
    if ans in indexes:
        task_entry = get_task_entry_by_idx(idx)
        task_entry.update(task)
        return update_task_entry_for_task_id(int(ans), task)
    else:
        raise Exception("Error: user chose an index that is not present for task name: {}".format(task_name))


def delete_task_entries(task_name):
    records, err = find_task_entries_for_task_name(task_name)
    if err is not None:
        return err
    indexes = {}
    items = "Please indicate which index you'd like to delete\n"
    for record in records:
        indexes[str(record[0])] = 0
        items += "{}: {}\n".format(record[0], record[1:])
    items += "or you can indicate (all/n) "
    ans = input(
        items
    )
    if ans in indexes:
        return delete_task_entry_for_task_id(int(ans))
    elif ans == "all":
        return delete_all_task_entries_for_task_name(task_name)
    elif ans == "n":
        print("Info: user cancelled delete entry for task name: {}".format(task_name))
    else:
        raise Exception("Error: user chose an index that is not present for task name: {}".format(task_name))
    return None


if __name__ == "__main__":
    weekly = Weekly(days_of_the_week=[DaysOfTheWeek.FRIDAY, DaysOfTheWeek.SATURDAY])
    if insert_task("leetcode") is not None:
        print("Error: insert in todo list did not insert properly")

    task = Task()
    task.habit = True

    err = update_task_entry("leetcode", task)
    if err is not None:
        print("{}".format(err))

    get_task_entries("leetcode")

    deleted_err = delete_task_entries("leetcode")
    if deleted_err is not None:
        print("{}".format(err))
