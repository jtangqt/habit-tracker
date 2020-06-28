from postgres import with_postgres_connection
from task import Task


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
            raise Exception("Error: record for task {} does not exist".format(idx))
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
