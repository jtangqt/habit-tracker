import calendar
from datetime import timedelta
import datetime
from json_record import JSONRecord
from occurrences import Occurrences


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
        # todo update start, end and due date

    def get_next_occurrence(self):
        if self.schedule_info["cadence"] == "once":
            return self.schedule_info["occurrences"].dates[0]

        elif self.schedule_info["cadence"] == "yearly":
            for date in self.schedule_info["occurrences"].dates:
                new_date = datetime.date(date.year, date.month, date.day)
                if new_date > datetime.date.today():
                    return new_date
            for date in self.schedule_info["occurrences"].dates:
                new_date = datetime.date(date.year + 1, date.month, date.day)
                if new_date > datetime.date.today():
                    return new_date

        elif self.schedule_info["cadence"] == "monthly":
            month = datetime.date.today().month
            year = datetime.date.today().year
            month_range = calendar.monthrange(year, month)[1]
            for day in self.schedule_info["occurrences"].dates:
                if isinstance(day, int) and day < month_range:
                    next_date = datetime.date(year, month, day)
                else:
                    next_date = datetime.date(year, month, month_range)
                if next_date > datetime.date.today():
                    return next_date
            # this is for next month
            for day in self.schedule_info["occurrences"].dates:
                next_month = month + 1
                if next_month > 12:
                    next_month = 1
                month_range = calendar.monthrange(year, next_month)[1]
                if isinstance(day, int) and day < month_range:
                    day = datetime.date(year, month + 1, day)
                else:
                    day = datetime.date(year, month + 1, month_range)
                if day > datetime.date.today():
                    return day

        elif self.schedule_info["cadence"] == "weekly":
            today = datetime.date.today()
            last_monday = today - datetime.timedelta(days=today.weekday())
            weekdays = []
            for i in range(14):
                weekdays.append(last_monday + datetime.timedelta(days=i))
            for day in self.schedule_info["occurrences"].dates:
                index = list(calendar.day_name).index(day)
                if weekdays[index] > today:
                    return weekdays[index]
            # for next week
            for day in self.schedule_info["occurrences"].dates:
                index = list(calendar.day_name).index(day)
                if weekdays[index + 7] > today:
                    return weekdays[index + 7]

        elif self.schedule_info["cadence"] == "daily":
            return datetime.date.today() + timedelta(days=1)

        else:
            raise Exception("Error: cadence does not exist: {}".format(self.schedule_info["cadence"]))

        # todo: get next occurrence if it's a number

