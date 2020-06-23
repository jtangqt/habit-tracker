import calendar
import datetime


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

    @staticmethod
    def is_numeric_occurrence(occurrence):
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
            week_days_dict = {i: 0 for i in calendar.day_name}
            for day_of_the_week in occurrences:
                if day_of_the_week not in week_days_dict:
                    return False
            self.update_occurrence(None, occurrences)
        return True

    @staticmethod
    def validate_and_save_daily_occurrence(occurrences):
        if len(occurrences) > 0:
            return False
        return True
