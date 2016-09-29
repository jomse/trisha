from enum import Enum


class Color(Enum):
    sBlue = '\033[1;34m'
    sCrimson = '\033[1;38m'
    sGray = '\033[1;30m'
    sMagenta = '\033[1;35m'
    sWight = '\033[1;m'
    sYellow = '\033[1;33m'
    sHRed = '\033[1;41m'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value