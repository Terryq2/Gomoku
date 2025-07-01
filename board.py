import random
import numpy
from timer import Timer
from utilities import CandidateManager, Point, Move, Candidate
from stones import Stone

class InvalidMoveError(Exception):
    pass

class NoMoveToCancelError(Exception):
    pass

class Move:
    def __init__(self, x: int, y: int, stone: Stone, candidates_added: list[Candidate]):
        self.point: Point =  Point(x, y)
        self.player: Stone = stone
        self.candidates_added: list[Candidate] = candidates_added
        self.took_candidate_place_white: bool = False
        self.took_candidate_place_black: bool = False

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.point.x == other.point.x 
                and self.point.y == other.point.y 
                and self.player == other.player)

    def __str__(self):
        if self.player == 1:
            return f"Point:({self.point.x},{self.point.y}), Player: White"
        else:
            return f"Point:({self.point.x},{self.point.y}), Player: Black"

class Board:
    def __init__(self, board_size):
        self.candidates_manager: CandidateManager = CandidateManager(board_size)
        
        self.min_x = float('inf')
        self.max_x = float('-inf')

        self.min_y = float('inf')
        self.max_y = float('-inf')
        
        self.current_player: int = Stone.WHITE
        self.board_size: int = board_size
        self.board: list[list[int]] = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.zobrist_table: list[list[list[int]]] = self.generate_zobrist_table()
        self.move_stack: list[Move] = []
        self.hash_for_board: int = 0
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

        self.pattern_score = {
            
            (1, 1, 1, 1, 1): 1000000, 

          
            (0, 1, 1, 1, 1, 0): 100000,       
            
            
            (1, 1, 1, 1, 0): 10000,               
            (0, 1, 1, 1, 1): 10000,
            (1, 1, 1, 0, 1): 10000,
            (1, 1, 0, 1, 1): 10000,
            (1, 0, 1, 1, 1): 10000,
            (0, 1, 1, 1, -1): 10000,
            (-1, 1, 1, 1, 0): 10000,

            
            (0, 1, 1, 1, 0): 5000,               
            (0, 1, 0, 1, 1, 0): 5000,            

           
            (1, 1, 1, 0): 1000,
            (0, 1, 1, 1): 1000,
            (1, 1, 0, 1, 0): 1000,
            (0, 1, 0, 1, 1): 1000,
            (0, 1, 1, 0, 1): 1000,

            
            (0, 1, 1, 0): 500,
            (0, 1, 0, 1, 0): 500,
     
            (1, 1, 0): 100,
            (0, 1, 1): 100,
            (1, 0, 1): 100,
        }


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


    def update_box(self, x: int, y: int):
        if x < self.min_x:
            self.min_x = x
        if x > self.max_x:
            self.max_x = x

        if y < self.min_y:
            self.min_y = y
        if y > self.max_y:
            self.max_y = y


    def place(self, x: int, y: int) -> bool:
        """Place a stone at (x,y) for the current player"""
        self.hash_for_board ^= self.zobrist_table[y][x][self.get_stone_index_for_hashing(self.board[y][x])] # hash out the original value
        self.hash_for_board ^= self.zobrist_table[y][x][self.get_stone_index_for_hashing(self.current_player)] #hash in the new value
        
        #Set board to have the current player at x,y
        self.board[y][x] = Stone.WHITE if self.current_player == Stone.WHITE else Stone.BLACK

        self.update_box(x, y)
        
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
                if self.board[candidate_point.y][candidate_point.x] == Stone.EMPTY and not self.candidates_manager.is_a_candidate(candidate_point, self.current_player):
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
        

        self.hash_for_board ^= self.zobrist_table[y][x][self.get_stone_index_for_hashing(self.board[y][x])] # hash out original value
        self.hash_for_board ^= self.zobrist_table[y][x][self.get_stone_index_for_hashing(Stone.EMPTY)] #hash in the new value

        self.board[y][x] = Stone.EMPTY

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
        
        self.board =  [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.move_stack = []
        self.candidates_manager = CandidateManager(self.board_size)
        self.hash_for_board = 0
        self.current_player = Stone.WHITE

        return True


    def check_win(self, x: int, y: int, player: Stone) -> bool:
        """Checks if a player has won"""
        return any(
            self.count_consecutive(x, y, dx, dy, player) == 5
            for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]  # horizontal, vertical, diag1, diag2
        )

    def count_consecutive(self, x: int, y: int, dx: int, dy: int, player: Stone) -> int:
        """Counts the number of consecutive stones vertically, horizontally and diagonally"""
        count = 1
        opponent = Stone(player * -1)

        for i in range(1, 5):
            if self.in_bounds(x + i * dx, y + i * dy):
                if self.board[y + i * dy][x + i * dx] == player:
                    count += 1
                elif self.board[y + i * dy][x + i * dx] == opponent or self.board[y + i * dy][x + i * dx] == Stone.EMPTY:
                    break

        for i in range(1, 5):
            if self.in_bounds(x - i * dx, y - i * dy):
                if self.board[y - i * dy][x - i * dx] == player:
                    count += 1
                elif self.board[y - i * dy][x - i * dx] == opponent or self.board[y - i * dy][x - i * dx] == Stone.EMPTY:
                    break

        return count

    def in_bounds(self, x: int, y: int) -> bool:
        """Returns whether a point is in bounds"""
        return 0 <= x < self.board_size and 0 <= y < self.board_size
    
    def evaluate_board(self) -> int:
        """Gives a score of the current board"""
        with Timer('Evaluation'):
            if self.hash_for_board in self.transposition_table:
                return self.transposition_table[self.hash_for_board]
            
            white_score = (self.evaluate_horizontals(Stone.WHITE) 
                        + self.evaluate_verticals(Stone.WHITE) 
                        + self.evaluate_diagonals(Stone.WHITE))


            black_score = (self.evaluate_horizontals(Stone.BLACK)
                        + self.evaluate_verticals(Stone.BLACK)
                        + self.evaluate_diagonals(Stone.BLACK))
     
            self.transposition_table[self.hash_for_board] = white_score - black_score
        return self.transposition_table[self.hash_for_board]
           

    def evaluate_left_diagonals(self, player: Stone) -> int:
        """Evaluate the possible left diagonals"""
        score = 0
        mid_line = self.board_size - 1
        for index in range(4, len(self.num_of_elements_in_left_diagonals)-4): 
            if self.num_of_elements_in_left_diagonals[index] >= 2:
                if index <= mid_line: 
                    start_y = -index + self.board_size  - 1
                    line = [self.board[start_y + i][i] for i in range(index + 1)]
                    score += self.score_line(line, player)
                
                else: 
                    start_x = index - self.board_size + 1
                    line = [self.board[i][start_x + i] for i in range(2 * mid_line + 1- index)]
                    score += self.score_line(line, player)   


        return score
    
    def evaluate_right_diagonals(self, player: Stone) -> int:
        """Evaluate the possible right diagonals"""
        score = 0
        mid_line = self.board_size - 1
        for index in range(4, len(self.num_of_elements_in_right_diagonals)-4): 
            if self.num_of_elements_in_right_diagonals[index] >= 2:
                if index <= mid_line: 
                    start_y = index
                    line = [self.board[start_y-i][i] for i in range(index + 1)]
                    score += self.score_line(line, player)
                
                else:
                    start_x = self.board_size - index + 1
                    line = [self.board[self.board_size-1-i][start_x + i] for i in range(2 * mid_line + 1- index)]
                    score += self.score_line(line, player)
            
        return score
    
    def evaluate_horizontals(self, player: Stone) -> int:
        """Evaluate the possible horizontals"""
        score = 0

        # for y in range(self.board_size):
        #     score += self.score_line(self.board[y], player)

        for y in range(self.min_y, self.max_y + 1):
            if self.num_of_elements_in_rows[y] >= 2:
                score += self.score_line(self.board[y], player)

        return score

    def evaluate_verticals(self, player: Stone) -> int:
        """Evaluate the possible verticals"""
        score = 0
        for x in range(self.min_x, self.max_x + 1):
            if self.num_of_elements_in_cols[x] >= 2:
                col = [self.board[y][x] for y in range(self.board_size)]
                score += self.score_line(col, player)

        return score
    
    def evaluate_diagonals(self, player: Stone) -> int:
        """Combining the score of the diagonal evaluations"""
        score = self.evaluate_left_diagonals(player)
        score += self.evaluate_right_diagonals(player)
        return score
    
    
    
    def score_line(self, line: list[Stone], player: Stone) -> float:
        stones = [(1 if s == player else -1 if s != Stone.EMPTY else 0) for s in line]
        score = 0
        max_len = max(len(pat) for pat in self.pattern_score)

        for window_size in range(3, max_len + 1):
            for i in range(len(stones) - window_size + 1):
                window = tuple(stones[i:i + window_size])
                if window in self.pattern_score:
                    val = self.pattern_score[window]
                    score += val
        return score

if __name__ == '__main__':
    print("Hello")