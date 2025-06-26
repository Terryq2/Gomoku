from enum import IntEnum
class Stone(IntEnum):
    EMPTY = 0
    BLACK = -1
    WHITE = 1

    def __str__(self):
        if self == Stone.EMPTY:
            return "Empty"
        elif self == Stone.BLACK:
            return "Black"
        elif self == Stone.WHITE:
            return "White"
