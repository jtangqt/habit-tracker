from datetime import datetime, timedelta
import json
import psycopg2

from postgres import start_connection, close_connection

BREAKFAST = "Breakfast"
LUNCH = "Lunch"
DINNER = "Dinner"
SNACKS = "Snack"
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
        self.snacks = {"name": SNACKS, "entries": []}
        self.midnight_snacks = {"name": MIDNIGHTSNACK, "entries": []}
    def update_meal(self, meal_type, food_entries):
        meal = self.meal_name_to_journal_entry(meal_type)
        meal['entries'].extend(food_entries)
    def meal_name_to_journal_entry(self, meal_type):
        switcher={
            BREAKFAST: self.breakfast,
            LUNCH: self.lunch,
            DINNER: self.dinner,
            SNACKS: self.snacks,
            MIDNIGHTSNACK: self.midnight_snacks,
        }
        return switcher.get(meal_type, "Invalid meal type")
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

def insert_new_journal_entry(journal_entry, date):
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
        print (count, "Info: Record inserted successfully into mobile table")
    except (Exception, psycopg2.Error) as error:
        return error
    close_connection(connection)
    return None

def get_journal_entry(dates):
    return dates

def update_journal_entry():
    return 0

def delete_journal_entry(date):
    return 0

#todo determine what to do with weight



journal_entry = journal_entry()
meal_entry = food("coffee", 3)
journal_entry.update_meal(BREAKFAST, [meal_entry])
date = datetime.date(datetime.now())
err = insert_new_journal_entry(journal_entry, date)
