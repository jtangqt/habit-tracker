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
def insert(cursor, date, journal_entry, operation_name="inserted", table_name="food_journal"):
    query = "select * from food_journal where date = %s"
    cursor.execute(query, (date,))
    record = cursor.fetchone()
    if record is not None:
        raise Exception("Error: record already exists")
    insert_entry = "insert into food_journal (date, data) values (%s,%s)"
    data = (date, journal_entry.to_json())
    cursor.execute(insert_entry, data)

@with_postgres_connection
def find(cursor, date, operation_name="found", table_name="food_journal"):
    try:
        query = "select * from food_journal where date = %s"
        cursor.execute(query, (date,))
        record = cursor.fetchone()
        if record is None:
            raise Exception("Error: record for date {} does not exist".format(date))
    except (Exception, psycopg2.Error) as error:
        return None, error
    return record, None

@with_postgres_connection
def update(cursor, date, entries, operation_name="updated", table_name="food_journal"):
    update_entry = "update food_journal set data =  %s where date = %s"
    data = (entries.to_json(), date)
    cursor.execute(update_entry, data)

@with_postgres_connection
def delete(cursor, id, operation_name="deleted", table_name="food_journal"):
    query = "delete from food_journal where id = %s"
    cursor.execute(query, (id,))

def insert_journal_entry(date, journal_entry):
     return insert(date, journal_entry)

def update_journal_entry(date, meal, food_entries):
    record, err = find(date)
    if err is not None:
        return err
    existing_entry = JournalEntry()
    existing_entry.unpack_json(record[2])
    new_entry = existing_entry
    new_entry.update_meal(meal, food_entries)
    return update(date, new_entry)

def get_journal_entry(date):
    record, err = find(date)
    if err is not None:
        return None, err
    entry = JournalEntry()
    entry.unpack_json(record[2])
    print("Info: got 1 record successfully")
    return entry, None

def delete_journal_entry(date):
    record, err = find(date)
    if err is not None:
        return err

    ans = input("\nAre you sure you want to delete entry {} for date: {}:\n{}\n(Y/n) ".format(record[0], record[1], record[2]))
    if ans == "Y":
        return delete(record[0])
    else:
        print("Info: user cancelled delete for entry {}".format(record[0]))
    return None

if __name__ == "__main__":
    entry = JournalEntry()
    food_1 = Food("coffee", 8)
    food_2 = Food("bagel", 300)
    date = datetime.date(datetime.now())# - timedelta(days=1)
    entry.update_meal(MealType.DINNER, [food_1])

    ## insert
    err = insert_journal_entry(date, entry)
    if err is not None:
        print("{}".format(err))

    ## update
    err = update_journal_entry(date, MealType.BREAKFAST, [food_1, food_2])
    if err is not None:
        print("{}".format(err))

    ## read
    entry, err = get_journal_entry(date)
    if err is not None:
        print("{}".format(err))
    print(entry)

    ## delete
    err = delete_journal_entry(date)
    if err is not None:
        print("{}".format(err))
