import calendar
from datetime import timedelta, time, date
import datetime

from ..helper import json_record
from postgres import with_postgres_connection


class Occurrences:
    def __init__(self):
        self.number = None,  # number of times
        self.dates = []
        # once -> datetime
        # yearly -> dates
        # monthly -> dates & last day of the month
        # weekly -> day of the week
        # daily -> None

    def update_occurrence(self, number, dates):
        self.number = number
        self.dates = dates

    def is_numeric_occurrence(self, occurrence):
        if isinstance(occurrence[0], datetime.date):
            return False
        return occurrence[0].isnumeric() and len(occurrence) == 1

    def validate_and_save_once_occurrence(self, occurrences):  # occurrences looks like [datetime]
        if len(occurrences) > 1 and not isinstance(occurrences[0], datetime.date):
            return False
        self.update_occurrence(None, occurrences[0])
        return True

    def validate_and_save_yearly_occurrence(self, occurrences):
        if self.is_numeric_occurrence(occurrences):
            self.update_occurrence(occurrences[0], [])
            return True
        else:
            for date in occurrences:
                if not isinstance(date, datetime.date):
                    return False
            self.update_occurrence(None, occurrences)
            return True

    def validate_and_save_monthly_occurrence(self, occurrences):
        if self.is_numeric_occurrence(occurrences):
            self.update_occurrence(occurrences[0], [])
            return True
        else:
            save_occurrence = []
            last_day = False
            for day_of_the_month in occurrences[1:]:
                if day_of_the_month == "Last Day":
                    last_day = True
                elif day_of_the_month <= 31:
                    save_occurrence.append(day_of_the_month)
                else:
                    return False
            if last_day:
                save_occurrence = ["Last Day"] + save_occurrence
            self.update_occurrence(None, save_occurrence)
        return True

    def validate_and_save_weekly_occurrence(self, occurrences):
        if self.is_numeric_occurrence(occurrences):
            self.update_occurrence(occurrences[0], [])
            return True
        else:
            week_days_dict = { i : 0 for i in calendar.day_name }
            for day_of_the_week in occurrences:
                if day_of_the_week not in week_days_dict:
                    return False
            self.update_occurrence(None, occurrences)
        return True

    def validate_and_save_daily_occurrence(self, occurrences):
        if len(occurrences) > 0:
            return False
        return True


class Schedule(JSONRecord):
    def __init__(self):
        self.schedule_info = {
            "cadence": "",  # once, yearly, monthly, weekly, daily
            "occurrences": Occurrences(),
            "start_date": None,
            "end_date": None,
            "due_date": None,
        }
        super().__init__(self.schedule_info)

    def validate_occurrence(self, cadence, occurrences):
        try:
            if cadence == "once":
                if not self.schedule_info["occurrences"].validate_and_save_once_occurrence(occurrences):
                    raise Exception("Error: validate occurrence failed and didn't save for cadence type: once")
            elif cadence == "yearly":
                if not self.schedule_info["occurrences"].validate_and_save_yearly_occurrence(occurrences):
                    raise Exception("Error: validate occurrence failed and didn't save for cadence type: yearly")
            elif cadence == "monthly":
                if not self.schedule_info["occurrences"].validate_and_save_monthly_occurrence(occurrences):
                    raise Exception("Error: validate occurrence failed and didn't save for cadence type: monthly")
            elif cadence == "weekly":
                if not self.schedule_info["occurrences"].validate_and_save_weekly_occurrence(occurrences):
                    raise Exception("Error: validate occurrence failed and didn't save for cadence type: weekly")
            elif cadence == "daily":
                if not self.schedule_info["occurrences"].validate_and_save_daily_occurrence(occurrences):
                    raise Exception("Error: validate occurrence failed and didn't save for cadence type: daily")
            else:
                raise Exception("Error: cadence does not exist: {}".format(cadence))
        except Exception as error:
            return error
        return None

    def update_schedule(self, cadence, occurrences):
        err = self.validate_occurrence(cadence, occurrences)
        if err is not None:
            return err
        self.schedule_info["cadence"] = cadence
        self.schedule_info["occurrences"] = occurrences
        # todo update start, end and due date


class Project(JSONRecord):
    def __init__(self):
        self.project_breakdown = {
            "project": "",
            "sub_project": "",
        }
        super().__init__(self.project_breakdown)
    # todo

class Task:
    def __init__(self):
        self.idx = None
        self.task_name = None
        self.created_on = None
        self.schedule = Schedule()
        self.is_complete = {}
        self.next_occurence = None
        self.project = Project()
        self.parent_task = None
        self.task_dependencies = {}
        self.related_tasks = {}  # this is for future use
        self.goal = ""
        self.habit = False  # this is for future use
        # determine how long it takes to complete related projects/tasks on average
        # to generate estimate for current project/task
        # self.time_spent = {date: timedelta} # this tracks how long I've spent on this task(s)

    def unpack_records(self, record):
        # questions: how do you enforce one element is one of those types
        for i, key in enumerate(self.__dict__):
            self.__dict__[key] = record[i]

    def update(self, task):
        for i, key in enumerate(self.__dict__):
            if task.__dict__[key] is not None:
                self.__dict__[key] = task.__dict__[key]
        # todo
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
                   'set task_name = %s, created_on = %s, schedule = %s ' \
                   'where idx = %s'
    data = (
        entries.task_name, entries.created_on, entries.schedule.to_json(),
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
    print("Info: got {} record successfully from task name".format(len(records)))
    return records, None


def get_task_entry_by_idx(idx):
    record, err = find_task_entry_for_task_id(idx)
    if err is not None:
        return None, err
    task_entry = Task()
    task_entry.unpack_records(record)
    print("Info: got 1 record successfully from idx: {}".format(idx))
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
        task_entry, _ = get_task_entry_by_idx(int(ans))
        task_entry.update(task)
        return update_task_entry_for_task_id(int(ans), task_entry)
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

    task = Task()
    today = date.today()
    err = task.schedule.validate_occurrence("weekly", ["Monday", "Wednesday", "Friday"])
    if err is not None:
        print("{}".format(err))

    # todo: what happens if i postpone a weekly cadence to tomorrow?
    if insert_task("leetcode") is not None:
        print("Error: insert in to-do list did not insert properly")

    err = update_task_entry("leetcode", task)
    if err is not None:
        print("{}".format(err))

    err = task.schedule.update_schedule("weekly", ["Monday"])
    if err is not None:
        print("{}".format(err))

    deleted_err = delete_task_entries("leetcode")
    if deleted_err is not None:
        print("{}".format(err))
