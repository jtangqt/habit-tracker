from enum import Enum

class NoValue(Enum):
    def __repr__(self):
        return "%s".format(self.value)