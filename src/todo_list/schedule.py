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
        self.schedule_info["occurrences"] = occurrences
        # todo update start, end and due date
