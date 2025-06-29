"""This module implements the board with bitwise operations for Gomoku"""

import random
from stones import Stone
from numba import njit
from scipy.signal import convolve2d
import numpy as np




class InvalidMoveError(Exception):
    pass

class InvalidStoneParameterError(Exception):
    pass
class BitBoard:
    """Board storing information as bits"""
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.white_rows = [0 for _ in range(board_size)]
        self.black_rows = [0 for _ in range(board_size)]
        self.zobrist_table: list[list[list[int]]] = self.generate_zobrist_table()
        self.hash_for_board: int = self.initialize_hashing_for_board()

    def reset(self):
        self.white_rows = [0 for _ in range(self.board_size )]
        self.black_rows = [0 for _ in range(self.board_size )]
        self.zobrist_table: list[list[list[int]]] = self.generate_zobrist_table()
        self.hash_for_board: int = self.initialize_hashing_for_board()

    
    def get_column(self, x: int, player: Stone) -> int:
        """Returns a int representing the column at index x"""
        mask = 1 << (self.board_size - 1 - x)
        alpha = sum((self.white_rows[y] & mask) != 0 << y for y in range(self.board_size))
        beta = sum((self.black_rows[y] & mask) != 0 << y for y in range(self.board_size))
        return (alpha, beta)
    
    def get_row(self, y: int, player: Stone) -> int:
        if player == Stone.WHITE:
            return self.white_rows[y]
        if player == Stone.BLACK:
            return self.black_rows[y]

    def get_left_diagonal(self, index: int, player: Stone) -> int:
        """Returns the index th left diagonal in bits form"""
        mid_line = self.board_size - 1
        opponent = player * -1
        if index <= mid_line: 
            start_y = -index + self.board_size  - 1
            alpha_line = 0b0
            beta_line = 0b0
            for i in range(index + 1):
                alpha_line |= self.get(i, start_y + i, player) << (index + 1 - i)
                beta_line |= self.get(i, start_y + i, opponent) << (index + 1 - i)
            return (alpha_line, beta_line)
        else: 
            start_x = index - self.board_size + 1
            alpha_line = 0b0
            beta_line = 0b0
            for i in range(2 * mid_line + 1 - index):
                alpha_line |= self.get(start_x + i, i, player) << (2 * mid_line + 1 - index - i - 1)
                beta_line |= self.get(start_x + i, i, opponent) << (2 * mid_line + 1 - index - i - 1)
            return (alpha_line, beta_line)
        
    
    def get_right_diagonal(self, index: int, player: Stone) -> int:
        mid_line = self.board_size - 1
        opponent = player * -1
        if index <= mid_line: 
            start_y = index
            alpha_line = 0b0
            beta_line = 0b0
            for i in range(index + 1):
                alpha_line |= self.get(i, start_y-i, player) << (index + 1 - i)
                beta_line |= self.get(i, start_y-i, opponent) << (index + 1 - i)
            return (alpha_line, beta_line)
        
        else:
            start_x = index - self.board_size + 1
            alpha_line = 0b0
            beta_line = 0b0
            for i in range(2 * mid_line + 1 - index):
                alpha_line |= self.get(start_x + i, self.board_size - 1 - i, player) << (2 * mid_line + 1- index - i - 1)
                beta_line |= self.get(start_x + i, self.board_size - 1 - i, opponent) << (2 * mid_line + 1- index - i - 1)
            return (alpha_line, beta_line)




    def is_empty(self, x: int, y: int) -> bool:
        """Checks if a location is empty"""
        if x < 0 or x > self.board_size:
            raise InvalidMoveError('Coordinates do not exist')
        if y < 0 or y > self.board_size:
            raise InvalidMoveError('Coordinates do not exist')
    
        mask = 1 << (self.board_size - 1 - x) 
        if self.white_rows[y] & mask or self.black_rows[y] & mask:
            return False
        return True

    def get(self, x: int, y: int, player: Stone) -> int:
        "gets the value of the board at x,y for player, returns"
        if player == Stone.WHITE:
            mask = 1 << (self.board_size - 1 - x) 
            if self.white_rows[y] & mask:
                return 1
            return 0
        
        mask = 1 << (self.board_size - 1 - x) 
        if self.black_rows[y] & mask:
            return 1
        return 0

    def place(self, x: int, y: int, player: Stone):
        "Places a stone at x,y"
        if y < 0 or y >= self.board_size:
            raise InvalidMoveError("Coordinates given are out of bounds.")
        
        if x < 0 or x >= self.board_size:
            raise InvalidMoveError("Coordinates given are out of bounds.")
        
        if self.white_rows[y] >> (self.board_size - 1 - x) & 1 == 1 and player == Stone.WHITE:
            raise InvalidMoveError('Position is non empty')
        
        if self.black_rows[y] >> (self.board_size - 1 - x) & 1 == 1 and player == Stone.BLACK:
            raise InvalidMoveError('Position is non empty')


        if player == Stone.WHITE:
            mask = 1 << (self.board_size - 1 - x) 
            self.white_rows[y] |= mask   
        else:
            mask = 1 << (self.board_size - 1 - x) 
            self.black_rows[y] |= mask
        
        self.hash_for_board ^= self.zobrist_table[y][x][0] # hash out the original value
        self.hash_for_board ^= self.zobrist_table[y][x][self.get_stone_index(self.get(x, y, player))] #hash in the new value\
    
    def remove(self, x: int, y: int, player: int):
        self.hash_for_board ^= self.zobrist_table[y][x][self.get_stone_index(self.get(x, y, player))] # hash out the original value
        self.hash_for_board ^= self.zobrist_table[y][x][0] #hash in the new value
    
        if player == Stone.WHITE:
            mask = ~(1 << (self.board_size - 1 - x))
            self.white_rows[y] &= mask   
        else:
            mask = ~(1 << (self.board_size - 1 - x))
            self.black_rows[y] &= mask
 
    def get_stone_index(self, stone: Stone):
        """Returns the index of the stone for hashing"""
        if stone == Stone.EMPTY:
            return 0
        if stone == Stone.BLACK: #Black
            return 1
        return 2 #White
        
    def generate_zobrist_table(self) -> list[list[int, int]]:
        """Generates a Zobrist table consisting of n times n times 3 different 64 bits"""
        output_table = [[[random.getrandbits(64) for _ in range(3)] for _ in range(self.board_size)] for _ in range(self.board_size)]
        return output_table
        
    def initialize_hashing_for_board(self) -> int:
        """The first hash of the board when no pieces are placed"""
        hashed_value = 0
        for y in range(self.board_size):
            for x in range(self.board_size):
                mask = 1 << (self.board_size - 1 - x)
                if self.black_rows[y] & mask == 1:
                    hashed_value ^= self.zobrist_table[y][x][self.get_stone_index(Stone.BLACK)]
                    continue
                if self.white_rows[y] & mask == 1:
                    hashed_value ^= self.zobrist_table[y][x][self.get_stone_index(Stone.WHITE)]
                    continue
                hashed_value ^= self.zobrist_table[y][x][self.get_stone_index(Stone.EMPTY)]
        return hashed_value
    
    def check_win(self, x: int, y: int, player: Stone) -> bool:
        """Checks if a player has won"""
        return any(
            self.count_consecutive(x, y, dx, dy, player) == 5
            for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]  # horizontal, vertical, diag1, diag2
        )

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns whether a point is in bounds"""
        return 0 <= x < self.board_size and 0 <= y < self.board_size
    
    def count_consecutive(self, x: int, y: int, dx: int, dy: int, player: Stone) -> int:
        """Counts the number of consecutive stones vertically, horizontally and diagonally"""
        count = 1

        for i in range(1, 5):
            if self.in_bounds(x + i * dx, y + i * dy):
                if self.get(x + i * dx, y + i * dy, player) == 1:
                    count += 1
                    continue
                else:
                    break

        for i in range(1, 5):
            if self.in_bounds(x - i * dx, y - i * dy):
                if self.get(x - i * dx, y - i * dy, player) == 1:
                    count += 1
                    continue
                else:
                    break

        return count

if __name__ == '__main__':
    board = BitBoard(15)
    board.place(1, 1, Stone.WHITE)

    board.has_five_in_a_row()