import enum
class Color(enum):
    setBlue = '\033[1;34m'
    setWight = '\033[1;m'


    def __str__(self):
        return self.value