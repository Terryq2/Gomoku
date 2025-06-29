import random
import numpy
from timer import Timer
from utilities import CandidateManager, Point, Move, Candidate
from stones import Stone
from bitboard import BitBoard

class InvalidMoveError(Exception):
    pass

class NoMoveToCancelError(Exception):
    pass

class Board:
    def __init__(self, board_size):
        self.candidates_manager: CandidateManager = CandidateManager(board_size)
        self.current_player: int = Stone.WHITE
        self.board_size: int = board_size
        self.bit_board: BitBoard = BitBoard(board_size)
        self.move_stack: list[Move] = []
        self.transposition_table: dict[int, int] = {}
        
        self.num_of_elements_in_rows: numpy.ndarray = numpy.zeros((self.board_size), dtype=int)
        self.num_of_elements_in_cols: numpy.ndarray = numpy.zeros((self.board_size), dtype=int)
        self.num_of_elements_in_left_diagonals: numpy.ndarray = numpy.zeros((2*self.board_size-1), dtype=int)
        self.num_of_elements_in_right_diagonals: numpy.ndarray = numpy.zeros((2*self.board_size-1), dtype=int)
        
        self.directions: list[tuple[int, int]] = [
            (-1, 0), #left
            (1, 0),  #right                        
            (0, 1), #down
            (0, -1), #up
            (-1, -1),#left up
            (1, -1), #right up
            (-1, 1), 
            (1, 1) #right down
        ]

    def get_stone_index_for_hashing(self, stone: Stone):
        """Returns the position for Zobrist hashing"""
        if stone == Stone.EMPTY:
            return 0
        if stone == Stone.BLACK:
            return 1
        if stone == Stone.WHITE:
            return 2
        
    def generate_zobrist_table(self) -> list[list[int, int]]:
        """Generates a Zobrist table consisting of n times n times 3 different 64 bits"""
        output_table = [[[random.getrandbits(64) for _ in range(3)] for _ in range(self.board_size)] for _ in range(self.board_size)]
        return output_table
        
    def initialize_hashing_for_board(self) -> int:
        """The first hash of the board when no pieces are placed"""
        hashed_value = 0
        for y in range(self.board_size):
            for x in range(self.board_size):
                stone = self.board[y][x]
                hashed_value ^= self.zobrist_table[y][x][self.get_stone_index_for_hashing(stone)]
        self.hash_for_board = hashed_value


    def place(self, x: int, y: int) -> bool:
        """Place a stone at (x,y) for the current player"""
        self.bit_board.place(x, y, self.current_player)
        
        #If placed at x,y then obviously that place can no longer be a candidate
        self.candidates_manager.candidate_points_black[y][x] = False
        self.candidates_manager.candidate_points_white[y][x] = False
        
        # Add candidates
        candidates_added = []
        for i in range(1, 3):
            for direction in self.directions:
                if not self.in_bounds(x + direction[0] * i, y+ direction[1] * i):
                    continue
                
                candidate_point = Point(x + direction[0] * i, y + direction[1] * i)
                if self.bit_board.is_empty(x + direction[0] * i, y + direction[1] * i) and not self.candidates_manager.is_a_candidate(candidate_point, self.current_player):
                    candidates_added.append(candidate_point)
                    self.candidates_manager.add_candidate_for_player(candidate_point, self.current_player)
                

        # Removing the candidate at the position which the stone is placed
        move_to_add = Move(x, y, self.current_player, candidates_added)

        if self.candidates_manager.remove_candidate_from_player(move_to_add.point, Stone.WHITE):
            move_to_add.took_candidate_place_white = True

        if self.candidates_manager.remove_candidate_from_player(move_to_add.point, Stone.BLACK):
            move_to_add.took_candidate_place_black = True
        
        self.move_stack.append(move_to_add)

        #Clean up and stats
        self.current_player = Stone(self.current_player * -1)

        self.num_of_elements_in_rows[y] += 1
        self.num_of_elements_in_cols[x] += 1
        
        right_diagonal_index = x + y
        left_diagonal_index = x - y + self.board_size - 1

        self.num_of_elements_in_right_diagonals[right_diagonal_index] += 1
        self.num_of_elements_in_left_diagonals[left_diagonal_index] += 1


        return True

    def cancel(self) -> bool:
        """Cancels the last move made"""
        if not self.move_stack:
            return
        
        last_move = self.move_stack.pop()
        player = last_move.player
        y = last_move.point.y
        x = last_move.point.x
        candidates_last_added =  last_move.candidates_added
        
        self.bit_board.remove(x, y, player)

        for candidate in candidates_last_added:
            self.candidates_manager.remove_candidate_from_player(candidate, player)
        
        if last_move.took_candidate_place_black:
            self.candidates_manager.add_candidate_for_player(Point(x, y), Stone.BLACK)
        if last_move.took_candidate_place_white:
            self.candidates_manager.add_candidate_for_player(Point(x, y), Stone.WHITE)
        
        self.current_player = Stone(-1*self.current_player)

        self.num_of_elements_in_rows[y] -= 1
        self.num_of_elements_in_cols[x] -= 1

        right_diagonal_index = x+y
        left_diagonal_index = x-y+self.board_size-1

        self.num_of_elements_in_right_diagonals[right_diagonal_index] -= 1
        self.num_of_elements_in_left_diagonals[left_diagonal_index] -= 1


        return True
    
    def reset(self) -> bool:
        """Resets the board"""
        if not self.move_stack:
            raise NoMoveToCancelError("No move to cancel.")
        
        self.bit_board.reset()
        self.move_stack = []
        self.candidates_manager = CandidateManager(self.board_size)
        self.hash_for_board = 0
        self.current_player = Stone.WHITE

        return True

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns whether a point is in bounds"""
        return 0 <= x < self.board_size and 0 <= y < self.board_size
    
    def evaluate_board(self) -> int:
        """Gives a score of the current board"""
        if self.bit_board.hash_for_board in self.transposition_table:
            return self.transposition_table[self.bit_board.hash_for_board]
        
        white_score = (self.evaluate_horizontals(Stone.WHITE) 
                    + self.evaluate_verticals(Stone.WHITE)
                    + self.evaluate_diagonals(Stone.WHITE))


        black_score = (self.evaluate_horizontals(Stone.BLACK)
                    + self.evaluate_verticals(Stone.BLACK)
                    + self.evaluate_diagonals(Stone.BLACK))
    
        self.transposition_table[self.bit_board.hash_for_board] = white_score - black_score
        return self.transposition_table[self.bit_board.hash_for_board]
           


    def stone_to_char(self, stones: list[Stone], player: Stone) -> list[str]:
        """Returns a string representation of a line of stones based on the player"""
        output = []
        for stone in stones:
            if stone == player:
                output.append('1')
            elif stone == Stone.EMPTY:
                output.append('0')
            else:
                output.append('X')
        return output

    def evaluate_left_diagonals(self, player: Stone) -> int:
        """Evaluate the possible left diagonals"""
        score = 0
        for index in range(4, len(self.num_of_elements_in_left_diagonals)-4): 
            if self.num_of_elements_in_left_diagonals[index] != 0:
                alpha_line, beta_line = self.bit_board.get_left_diagonal(index, player)
                score += self.score_line(alpha_line, beta_line)
                
        return score
    
    def evaluate_right_diagonals(self, player: Stone) -> int:
        """Evaluate the possible right diagonals"""
        score = 0
        for index in range(4, len(self.num_of_elements_in_right_diagonals)-4): 
            if self.num_of_elements_in_right_diagonals[index] != 0:
                alpha_line, beta_line = self.bit_board.get_right_diagonal(index, player)
                score += self.score_line(alpha_line, beta_line)

        return score
    
    def evaluate_horizontals(self, player: Stone) -> int:
        """Evaluate the possible horizontals"""
        score = 0
        opponent = player * -1
        for y in range(len(self.num_of_elements_in_rows)):
            if self.num_of_elements_in_rows[y] != 0:

                alpha_line = self.bit_board.get_row(y, player)
                beta_line = self.bit_board.get_row(y, opponent)

                score += self.score_line(alpha_line, beta_line)

        return score

    def evaluate_verticals(self, player: Stone) -> int:
        """Evaluate the possible verticals"""
        score = 0
        for x in range(len(self.num_of_elements_in_cols)):
            if self.num_of_elements_in_cols[x] != 0:

                alpha, beta = self.bit_board.get_column(x, player)

                score += self.score_line(alpha, beta)

        return score
    
    def evaluate_diagonals(self, player: Stone) -> int:
        """Combining the score of the diagonal evaluations"""
        score = self.evaluate_left_diagonals(player)
        score += self.evaluate_right_diagonals(player)
        return score
    
    def score_line(self, alpha: int, beta: int) -> float:
        """Scores a line"""

        #check win
        possible_iterations = self.board_size - 0b11111.bit_length()
        for i in range(possible_iterations):
            mask = 0b11111 << i
            if mask & alpha == mask:
                return 100000000
            
        patterns = [
            (0b011110, 100000),
            (0b01110, 10000),
            (0b0110, 1000)
        ]

        score = 0
        for pattern, value in patterns:
            possible_iterations = self.board_size - pattern.bit_length() + 1
            #Two edge cases
            mask = pattern >> 1
            left_bit = (0b1 << mask.bit_length())
            left_blocked = beta & left_bit
            if mask & alpha == mask:
                if not left_blocked:
                    score += value * 0.5
                else:
                    score += value * 0.1
            
            mask = pattern << (possible_iterations - 1)
            right_bit = (possible_iterations - 1)
            right_blocked = beta & right_bit
            if mask & alpha == mask:
                if not right_blocked:
                    score += value * 0.5
                else:
                    score += value * 0.1
            
            length = pattern.bit_length()
            for i in range(possible_iterations):
                mask = pattern << i
                if mask & alpha == mask:
                    left_bit = (0b1 << i + length)
                    right_bit = (0b1 << i)
                    check = beta & (left_bit | right_bit)
            
                    
                    if check == (left_bit | right_bit):
                        score += value * 0.1
                        continue

                    if check == left_bit or check == right_bit:
                        score += value * 0.5
                        continue

                    if check == 0b0:
                        score += value
                        continue
        return score


if __name__ == '__main__':
    print("Hello")