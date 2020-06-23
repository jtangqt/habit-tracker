from json_record import JSONRecord

class Project(JSONRecord):
    def __init__(self):
        self.project_breakdown = {
            "project": "",
            "sub_project": "",
        }
        super().__init__(self.project_breakdown)
    # todo
