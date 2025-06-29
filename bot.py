from strategies import minimax


class Bot:
    def __init__(self):
        self.minimax: minimax.Minimax = minimax.Minimax()


if __name__ == "__main__":
    n = 0b011110
    n = n << 5
    left_bit = 0b1 << 5 + 5
    right_bit = 0b1 << 5

    print(f"{n:016b}") 
    print(f"{left_bit:016b}") 
    print(f"{right_bit:016b}") 