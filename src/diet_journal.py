from datetime import datetime, timedelta, time, date
from enum import Enum
import json
import pytz

from postgres import with_postgres_connection


class NoValue(Enum):
    def __repr__(self):
        return "%s".format(self.value)


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
        return json.dumps(self.entries_by_meal_type, default=lambda o: o.__dict__)

    def unpack_json(self, record):
        try:
            self.entries_by_meal_type.update(record)
        except:
            print("Info: no meals for this day")


class Measurements():
    def __init__(self):
        self.entries_for_body_type = {
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
        return json.dumps(self.entries_for_body_type, default=lambda o: o.__dict__)

    def unpack_json(self, record):
        try:
            self.entries_for_body_type.update(record)
        except:
            print("Info: no measurements for this day")

    def update_with_new_if_not_none(self, new_record):
        for body_type in self.entries_for_body_type:
            if new_record.entries_for_body_type[body_type] is not None:
                self.entries_for_body_type[body_type] = new_record.entries_for_body_type[body_type]


class Exercise():
    def __init__(self):
        self.exercise = {
            "minutes": 0,
            "accomplishments": ""
        }

    def to_json(self):
        return json.dumps(self.exercise, default=lambda o: o.__dict__)

    def unpack_json(self, record):
        try:
            self.exercise.update(record)
        except:
            print("Info: no exercise for this day")

    def update_with_new_if_not_none(self, minutes, accomplishments):
        if minutes:
            self.exercise["minutes"] = minutes
        if accomplishments != "":
            self.exercise["accomplishments"] = accomplishments


class DietEntry():
    def __init__(self):
        self.journal_entry = JournalEntry()
        self.fasting_start_time = None
        self.weight = None
        self.measurements = Measurements()
        self.water = 0
        self.exercise = Exercise()

    def unpack_records(self, record):
        food_entry = JournalEntry()
        measurements = Measurements()
        exercise = Exercise()
        food_entry.unpack_json(record[1])
        measurements.unpack_json(record[3])
        exercise.unpack_json(record[6])
        self.journal_entry = food_entry
        self.measurements = measurements
        self.weight = record[2]
        self.fasting_start_time = record[4]
        self.water = record[5]
        self.exercise = exercise


@with_postgres_connection
def insert_row_if_not_empty(cursor, date, operation_name="inserted", table_name="diet_journal"):
    query = 'select * from diet_journal where date = %s'
    cursor.execute(query, (date,))
    record = cursor.fetchone()
    if record is not None:
        raise Exception("Error: record already exists")
    insert_entry = 'insert into diet_journal (date) values (%s)'
    cursor.execute(insert_entry, (date,))


@with_postgres_connection
def find_diet_entry_for_date(cursor, date, operation_name="found", table_name="diet_journal"):
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
def update_diet_entry_for_date(cursor, date, entries: DietEntry, operation_name="updated",
                               table_name="diet_journal"):
    update_entry = 'update diet_journal ' \
                   'set "Food Journal" = %s, "Weight (kg)" = %s, "Measurements" = %s, ' \
                   '"Fasting Start Time" = %s, "Exercise" = %s' \
                   'where date = %s'
    data = (
        entries.journal_entry.to_json(), entries.weight, entries.measurements.to_json(),
        entries.fasting_start_time, entries.exercise.to_json(),
        date)
    cursor.execute(update_entry, data)


@with_postgres_connection
def delete_diet_entry_for_date(cursor, date, operation_name="deleted", table_name="diet_journal"):
    query = 'delete from diet_journal where date = %s'
    cursor.execute(query, (date,))


def insert_diet_entry(date):
    return insert_row_if_not_empty(date)


def get_diet_entry(date):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return None, err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    print("Info: got 1 record successfully")
    return diet_entry, None


def delete_diet_entry(date):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err

    ans = input(
        "\nAre you sure you want to delete entry for date: {}:\n".format(record[0]) +
        "Food Journal: {}\n".format(record[1]) +
        "Weight: {}\n".format(record[2]) +
        "Measurements: {}\n".format(record[3]) +
        "Fasting Start Time: {}\n".format(record[4]) +
        "Water: {}\n".format(record[5]) +
        "Exercise: {}\n(Y/n)".format(record[6]))
    if ans == "Y":
        return delete_diet_entry_for_date(date)
    else:
        print("Info: user cancelled delete entry for date {}".format(record[0]))
    return None


def update_food_entry_for_date(date, meal, food_entries):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    diet_entry.journal_entry.update_meal(meal, food_entries)
    return update_diet_entry_for_date(date, diet_entry)


def update_weight_entry_for_date(date, weight):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    if diet_entry.weight != weight:
        diet_entry.weight = weight
        return update_diet_entry_for_date(date, diet_entry)
    print("Info: not updating since weight is the same")
    return None


def update_fasting_start_time_for_date(date, fasting_start_time, timezone):
    time_with_timezone = timezone.localize(fasting_start_time)
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    if diet_entry.fasting_start_time != None:
        print(
            "Info: changing fasting start time from {} to {}".format(diet_entry.fasting_start_time, time_with_timezone))
    else:
        print("Info: adding new fasting start time: {}".format(time_with_timezone))
    diet_entry.fasting_start_time = time_with_timezone
    return update_diet_entry_for_date(date, diet_entry)


def update_measurements_for_date(date, measurements):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    existing_measurements = diet_entry.measurements
    existing_measurements.update_with_new_if_not_none(measurements)
    return update_diet_entry_for_date(date, diet_entry)


def update_increased_water_intake(date, cups):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    diet_entry.water += cups
    return update_diet_entry_for_date(date, diet_entry)


def update_increased_water_intake_by_one_cup(date):
    return update_increased_water_intake(date, 1)


def update_water_total_cups_for_date(date, cups):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    diet_entry.water = cups
    return update_diet_entry_for_date(date, diet_entry)


def update_exercise_for_date(date, minutes, accomplishments=""):
    record, err = find_diet_entry_for_date(date)
    if err is not None:
        return err
    diet_entry = DietEntry()
    diet_entry.unpack_records(record)
    diet_entry.exercise.update_with_new_if_not_none(minutes, accomplishments)
    return update_diet_entry_for_date(date, diet_entry)


if __name__ == "__main__":
    entry = JournalEntry()
    food_1 = Food("coffee", 8)
    food_2 = Food("bagel", 300)
    date = date.today() - timedelta(days=4)
    entry.update_meal(MealType.DINNER, [food_1])

    ## insert
    err = insert_diet_entry(date)
    if err is not None:
        print("{}".format(err))

    # update food
    err = update_food_entry_for_date(date, MealType.BREAKFAST, [food_1, food_2])
    if err is not None:
        print("{}".format(err))

    ## update weight
    err = update_weight_entry_for_date(date, 55.9)
    if err is not None:
        print("{}".format(err))

    ## update fasting start time
    fasting_start_time = datetime(date.year, date.month, date.day, hour=22, minute=33)
    # timezone = pytz.timezone("America/New_York")
    timezone = pytz.timezone("America/Los_Angeles")
    err = update_fasting_start_time_for_date(date, fasting_start_time, timezone)
    if err is not None:
        print("{}".format(err))

    ## update measurements
    measurements = Measurements()
    measurements.entries_for_body_type[BodyType.WAIST] = 27
    err = update_measurements_for_date(date, measurements)
    if err is not None:
        print("{}".format(err))

    minutes = 2
    accomplisments = "literally did nothing today"
    err = update_exercise_for_date(date, minutes, accomplisments)
    if err is not None:
        print("{}".format(err))

    ## read
    entry, err = get_diet_entry(date)
    if err is not None:
        print("{}".format(err))

    ## delete
    err = delete_diet_entry(date)
    if err is not None:
        print("{}".format(err))
