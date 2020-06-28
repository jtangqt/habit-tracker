from datetime import date
from task import Task

from todo_list_db import *


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
