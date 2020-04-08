from datetime import datetime, timedelta
from enum import Enum
import json
import psycopg2

from postgres import with_postgres_connection, start_connection, close_connection


class NoValue(Enum):
    def __repr__(self):
        return '%s' % self.value


class Food:
    def __init__(self, name="", calories=0):
        self.name = name
        self.calories = calories


class MealType(str, NoValue):
    BREAKFAST = 'Breakfast'
    LUNCH = 'Lunch'
    DINNER = 'Dinner'
    SNACK = 'Snack'
    MIDNIGHTSNACK = 'Midnight Snack'

class JournalEntry():
    def __init__(self):
        self.entries_by_meal_type = {
            MealType.BREAKFAST: [],
            MealType.LUNCH: [],
            MealType.DINNER: [],
            MealType.SNACK: [],
            MealType.MIDNIGHTSNACK: [],
        }

    def update_meal(self, meal_type, food_entries):
        self.entries_by_meal_type[meal_type].extend(food_entries)

    def to_json(self):
        return json.dumps(self.entries_by_meal_type, default=lambda o: o.__dict__, indent=4)

    def unpack_json(self, record):
        self.entries_by_meal_type.update(record)

@with_postgres_connection
def insert_new_journal_entry(cursor, date, journal_entry, operation_name):
    query = "select * from food_journal where date = %s"
    cursor.execute(query, (date,))
    record = cursor.fetchone()
    if record is not None:
        raise Exception("Error: record already exists")
    insert_entry = "insert into food_journal (date, data) values (%s,%s)"
    data = (date, journal_entry.to_json())
    cursor.execute(insert_entry, data)
#
# @with_postgres_connection
# def get_journal_entry(cursor, date, name):
#     query = "select * from food_journal where date = %s"
#     cursor.execute(query, (date,))
#     record = cursor.fetchone()
#     if record is None:
#         raise Exception("Error: record for date {} does not exist".format(date))
#     print(record)
#     record_entry = JournalEntry()
#     print("hehe ",record_entry.entries_by_meal_type)
#     record_entry.unpack_json(record[2])
#     return entry, None

def get_journal_entry(date):
    connection, err = start_connection()
    if err is not None:
        return None, err
    try:
        cursor = connection.cursor()
        query = "select * from food_journal where date = %s"
        cursor.execute(query, (date,))
        record = cursor.fetchone()
        if record is None:
            raise Exception("Error: record for date {} does not exist".format(date))
        entry = JournalEntry()
        entry.unpack_json(record[2])
        print("Info: got 1 record successfully")
    except (Exception, psycopg2.Error) as error:
        return None, error
    close_connection(connection)
    return entry, None

@with_postgres_connection
def update_journal_entry(cursor, date, meal, food_entries, operation_name):
    query = "select * from food_journal where date = %s"
    cursor.execute(query, (date,))
    record = cursor.fetchone()
    if record is None:
        raise Exception("Error: record for date {} does not exist".format(date))
    existing_entry = JournalEntry()
    existing_entry.unpack_json(record[2])
    new_entry = existing_entry
    new_entry.update_meal(meal, food_entries)
    update_entry = "update food_journal set data =  %s where date = %s"
    data = (new_entry.to_json(), date)
    cursor.execute(update_entry, data)


#todo: split into 2 parts the select statement & the delete statement (if it is delete)
#todo: take select statement and add it into read, update & delete 
@with_postgres_connection
def delete_journal_entry(cursor, date, operation_name):
    query = "select * from food_journal where date = %s"
    cursor.execute(query, (date,))
    record = cursor.fetchone()
    if record is None:
        raise Exception("Error: record for date {} does not exist".format(date))
    ans = input("\nAre you sure you want to delete entry {} for date: {}:\n{}\n(Y/n) ".format(record[0], record[1],
                                                                                              record[2]))
    if ans == "Y":
        query = "delete from food_journal where id = %s"
        id = record[0]
        cursor.execute(query, (id,))
    else:
        # print("Info: user cancelled delete for entry {}".format(record[0]))
        operation_name = "cancelled delete for entry {}".format(record[0])

# todo determine what to do with weight

if __name__ == "__main__":
    entry = JournalEntry()
    food_1 = Food("coffee", 8)
    food_2 = Food("bagel", 300)
    date = datetime.date(datetime.now()) - timedelta(days=1)
    entry.update_meal(MealType.DINNER, [food_1])

    ## insert
    err = insert_new_journal_entry(date, entry, "inserted into food_journal")
    if err is not None:
        print("{}".format(err))

    ## update
    err = update_journal_entry(date, MealType.BREAKFAST, [food_1, food_2], "updated in food_journal")
    if err is not None:
        print("{}".format(err))

    ## read
    # entry, err = get_journal_entry(date, "read from food_journal")
    # if err is not None:
    #     print("{}".format(err))
    # print("wow: ", entry.entries_by_meal_type[MealType.DINNER])

    ## delete
    err = delete_journal_entry(date, "deleted in food_journal")
    if err is not None:
        print("{}".format(err))
