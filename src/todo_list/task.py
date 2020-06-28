from project import Project
from schedule import Schedule


class Task:
    def __init__(self):
        self.idx = None
        self.task_name = None
        self.created_on = None
        self.schedule = Schedule()
        self.is_complete = {}
        self.next_occurrence = None
        self.project = Project()
        self.parent_task = None
        self.task_dependencies = {}
        self.related_tasks = {}  # this is for future use
        self.goal = ""
        self.habit = False  # this is for future use
        # determine how long it takes to complete related projects/tasks on average
        # to generate estimate for current project/task
        # self.time_spent = {date: timedelta} # this tracks how long I've spent on this task(s)

    def unpack_records(self, record):
        # questions: how do you enforce one element is one of those types
        for i, key in enumerate(self.__dict__):
            self.__dict__[key] = record[i]

    def update(self, task):
        for i, key in enumerate(self.__dict__):
            if task.__dict__[key] is not None:
                self.__dict__[key] = task.__dict__[key]
        # todo
        return None
