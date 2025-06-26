from strategies import minimax


class Bot:
    def __init__(self):
        self.minimax: minimax.Minimax = minimax.Minimax()


if __name__ == "__main__":
    bot: Bot = Bot()