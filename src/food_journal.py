from datetime import datetime, timedelta
import json
import psycopg2
from collections import namedtuple

from postgres import start_connection, close_connection

BREAKFAST = "Breakfast"
LUNCH = "Lunch"
DINNER = "Dinner"
SNACK = "Snack"
MIDNIGHTSNACK = "Midnight Snack"

class food:
    def __init__(self, name="", calories=0):
        self.name = name
        self.calories = calories

class journal_entry:
    def __init__(self):
        self.breakfast = {"name": BREAKFAST, "entries": []}
        self.lunch = {"name": LUNCH, "entries": []}
        self.dinner = {"name": DINNER, "entries": []}
        self.snack = {"name": SNACK, "entries": []}
        self.midnight_snack = {"name": MIDNIGHTSNACK, "entries": []}
    def update_meal(self, meal_type, food_entries):
        meal = self.meal_name_to_journal_entry(meal_type)
        meal['entries'].extend(food_entries)
    def meal_name_to_journal_entry(self, meal_type):
        switcher={
            BREAKFAST: self.breakfast,
            LUNCH: self.lunch,
            DINNER: self.dinner,
            SNACK: self.snack,
            MIDNIGHTSNACK: self.midnight_snack,
        }
        return switcher.get(meal_type, "Invalid meal type")
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def unpack(self, record):
        self.breakfast = record['breakfast']
        self.lunch = record['lunch']
        self.dinner = record['dinner']
        self.snack = record['snack']
        self.midnight_snack = record['midnight_snack']

def insert_new_journal_entry(date, journal_entry):
    connection, err = start_connection()
    if err is not None:
        return err
    try:
        cursor = connection.cursor()

        query = "select * from food_journal where date = %s"
        cursor.execute(query, (date, ))
        record = cursor.fetchone()
        if record is not None:
            raise Exception("Error: record already exists")

        insert_entry = "insert into food_journal (date, data) values (%s,%s)"
        data = (date, journal_entry.toJSON())
        cursor.execute(insert_entry, data)
        connection.commit()
        count = cursor.rowcount
        print (count, "Info: Record inserted successfully into table")
    except (Exception, psycopg2.Error) as error:
        return error
    close_connection(connection)
    return None

def get_journal_entry(date):
    connection, err = start_connection()
    if err is not None:
        return None, err
    try:
        cursor = connection.cursor()
        query = "select * from food_journal where date = %s"
        cursor.execute(query, (date, ))
        record = cursor.fetchone()
        if record is None:
            raise Exception("Error: record for date {} does not exist".format(date))
        entry = journal_entry()
        entry.unpack(record[2])
        print("Info: Got 1 record successfully")
    except (Exception, psycopg2.Error) as error:
        return None, error
    close_connection(connection)
    return entry, None

def update_journal_entry(date, meal, food_entries):
    connection, err = start_connection()
    if err is not None:
        return err
    try:
        cursor = connection.cursor()
        query = "select * from food_journal where date = %s"
        cursor.execute(query, (date, ))
        record = cursor.fetchone()
        if record is None:
            raise Exception("Error: record for date {} does not exist".format(date))
        existing_entry = journal_entry()
        existing_entry.unpack(record[2])
        new_entry = existing_entry
        new_entry.update_meal(meal, food_entries)
        update_entry = "update food_journal set data =  %s where date = %s"
        data = (new_entry.toJSON(), date)
        cursor.execute(update_entry, data)
        connection.commit()
        count = cursor.rowcount
        print("Info: {} Record updated successfully".format(count))
    except (Exception, psycopg2.Error) as error:
        return error
    close_connection(connection)
    return None

def delete_journal_entry(date):
    return 0

#todo determine what to do with weight

if __name__ == "__main__":
    entry = journal_entry()
    food_1 = food("coffee", 8)
    food_2 = food("bagel", 300)
    date = datetime.date(datetime.now()) - timedelta(days = 1)
    entry.update_meal(DINNER, [food_1])
    ## insert
    # err = insert_new_journal_entry(date, entry)
    # if err is not  None:
    #    print("{}".format(err))
    ## update
    # err = update_journal_entry(date, BREAKFAST, [food_1, food_2])
    # if err is not None:
    #     print("{}".format(err))
    ## read
    entry, err = get_journal_entry(date)
    if err is not None:
        print("{}".format(err))
    print(entry.breakfast)
