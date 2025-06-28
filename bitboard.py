"""This module implements the board with bitwise operations for Gomoku"""

import random
from stones import Stone


class InvalidMoveError(Exception):
    pass
class BitBoard:
    """Board storing information as bits"""
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.white_rows = [0 for _ in range(board_size)]
        self.black_rows = [0 for _ in range(board_size)]
        self.zobrist_table: list[list[list[int]]] = self.generate_zobrist_table()
        self.hash_for_board: int = self.initialize_hashing_for_board()
    
    def get(self, x: int, y: int, player: Stone) -> int:
        "gets the value of the board at x,y for player, returns "
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
        
        if self.white_rows[y] >> (self.board_size - 1 - x) & 1 == 1:
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
        if player == Stone.WHITE:
            mask = ~(1 << (self.board_size - 1 - x))
            self.white_rows[y] &= mask   
        else:
            mask = ~(1 << (self.board_size - 1 - x))
            self.black_rows[y] &= mask

        self.hash_for_board ^= self.zobrist_table[y][x][self.get_stone_index(self.get(x, y, player))] # hash out the original value
        self.hash_for_board ^= self.zobrist_table[y][x][0] #hash in the new value\
        
    def get_stone_index(self, stone: Stone):
        """Returns the index of the stone for hashing"""
        if stone == 0:
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
        self.hash_for_board = hashed_value

if __name__ == '__main__':
    print(0b001)