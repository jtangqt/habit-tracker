from datetime import datetime, timedelta
from enum import Enum
import json

from postgres import with_postgres_connection


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


class BodyType(str, NoValue):
    HIPS = 'Hips'
    WAIST = 'Waist'
    BUST = 'Bust'
    LEFTARM = 'Left Arm'
    RIGHTARM = 'Right Arm'
    LEFTTHIGH = 'Left Thigh'
    RIGHTTHIGH = 'Right Thigh'
    NECK = 'Neck'


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
        try:
            self.entries_by_meal_type.update(record)
        except:
            print("Info: no meals for this day")


class Measurements():
    def __init__(self):
        self.measurements = {
            BodyType.HIPS: None,
            BodyType.WAIST: None,
            BodyType.BUST: None,
            BodyType.LEFTARM: None,
            BodyType.RIGHTARM: None,
            BodyType.LEFTTHIGH: None,
            BodyType.RIGHTTHIGH: None,
            BodyType.NECK: None,
        }
    def to_json(self):
        return json.dumps(self.measurements, default=lambda o: o.__dict__, indent=4)

    def unpack_json(self, record):
        try:
            self.measurements.update(record)
        except:
            print("Info: no measurements for this day")


class DietEntry():
    def __init__(self):
        self.journal_entry = JournalEntry()
        self.fasting_start_time = None
        self.weight = None
        self.measurements = Measurements()
    def unpack_records(self, record):
        food_entry = JournalEntry()
        measurements = Measurements()
        food_entry.unpack_json(record[2])
        measurements.unpack_json(record[4])
        self.journal_entry = food_entry
        self.measurements = measurements
        self.weight = record[3]
        self.fasting_start_time = record[5]


@with_postgres_connection
def insert(cursor, date, operation_name="inserted", table_name="diet_journal"):
    query = 'select * from diet_journal where date = %s'
    cursor.execute(query, (date,))
    record = cursor.fetchone()
    if record is not None:
        raise Exception("Error: record already exists")
    insert_entry = 'insert into diet_journal (date) values (%s)'
    cursor.execute(insert_entry, (date,))


@with_postgres_connection
def find(cursor, date, operation_name="found", table_name="diet_journal"):
    try:
        query = 'select * from diet_journal where date = %s'
        cursor.execute(query, (date,))
        record = cursor.fetchone()
        if record is None:
            raise Exception("Error: record for date {} does not exist".format(date))
    except (Exception, psycopg2.Error) as error:
        return None, error
    return record, None


@with_postgres_connection
def update(cursor, date, entries: DietEntry, operation_name="updated", table_name="diet_journal"):
    update_entry = 'update diet_journal ' \
                   'set data = %s, "Weight (kg)" = %s, "Measurements" = %s, "Fasting Start Time" = %s ' \
                   'where date = %s'
    data = (
    entries.journal_entry.to_json(), entries.weight, entries.measurements.to_json(), entries.fasting_start_time, date)
    cursor.execute(update_entry, data)


@with_postgres_connection
def delete(cursor, id, operation_name="deleted", table_name="diet_journal"):
    query = 'delete from diet_journal where id = %s'
    cursor.execute(query, (id,))


def insert_diet_entry(date):
    err = insert(date)
    if err is not None:
        return err


def get_diet_entry(date):
    record, err = find(date)
    if err is not None:
        return None, err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    print("Info: got 1 record successfully")
    return diet_entry, None


def delete_diet_entry(date):
    record, err = find(date)
    if err is not None:
        return err

    ans = input(
        "\nAre you sure you want to delete entry {} for date: {}:\n".format(record[0], record[1]) +
        "Food Journal: {}\n".format(record[2]) +
        "Weight: {}\n".format(record[3]) +
        "Fasting Start Time: {}\n".format(record[5]) +
        "Measurements: {}\n(Y/n)".format(record[4]))
    if ans == "Y":
        return delete(record[0])
    else:
        print("Info: user cancelled delete for entry {}".format(record[0]))
    return None


def update_food_entry(date, meal, food_entries):
    record, err = find(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    diet_entry.journal_entry.update_meal(meal, food_entries)
    return update(date, diet_entry)


def update_weight_entry(date, weight):
    record, err = find(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    if diet_entry.weight != weight:
        diet_entry.weight = weight
        return update(date, diet_entry)
    print("Info: not updating since weight is the same")
    return None


if __name__ == "__main__":
    entry = JournalEntry()
    food_1 = Food("coffee", 8)
    food_2 = Food("bagel", 300)
    date = datetime.date(datetime.now()) + timedelta(days=1)
    entry.update_meal(MealType.DINNER, [food_1])

    ## insert
    err = insert_diet_entry(date)
    if err is not None:
        print("{}".format(err))

    # update food
    err = update_food_entry(date, MealType.BREAKFAST, [food_1, food_2])
    if err is not None:
        print("{}".format(err))

    ## update weight
    err = update_weight_entry(date, 55.9)
    if err is not None:
        print("{}".format(err))

    ## read
    entry, err = get_diet_entry(date)
    if err is not None:
        print("{}".format(err))
    print(entry.weight)

    ## delete
    err = delete_diet_entry(date)
    if err is not None:
        print("{}".format(err))
