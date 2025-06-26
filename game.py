from board import Board
from user_interface import UI
from bot import Bot

class Gomoku:
    def __init__(self, board_size: int):
        self.board: Board = Board(board_size)
        self.bot: Bot = Bot() 
        self.user_interface: UI = UI(self.board, self.bot)
        
    
if __name__ == "__main__":
    game = Gomoku(19)
    # board: Board = Board(19)
    # board.place(2,2)

    # for candidate in board.candidates_manager.candidates_added_white:
    #     print(candidate)

    # board.place(3,3)
    # board.cancel()

    # for candidate in board.candidates_manager.candidates_added_white:
    #     print(candidate)