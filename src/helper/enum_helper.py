from enum import Enum

class XEnum(Enum):
    def __repr__(self):
        return "%s".format(self.value)