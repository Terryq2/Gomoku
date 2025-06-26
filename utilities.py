import numpy
from stones import Stone

class Candidate:
    def __init__(self, x: int, y: int, stone: Stone):
        self.point: Point =  Point(x, y)
        self.player: Stone = stone

    def __str__(self):
        return f'({self.point.x}, {self.point.y})'

class Frame:
    def __init__(self,
                 depth: int,
                 player: Stone,
                 candidate_index: int,
                 candidates: list[Candidate],
                 current_candidate: Candidate):
        self.depth = depth
        self.player = player
        self.candidate_index = candidate_index
        self.candidates = candidates
        self.best_score = float('-inf') if player == Stone.WHITE else float('inf')
        self.current_candidate = current_candidate
        self.best_candidate = None

class Move:
    "A class simulating a move on a Gomoku board"
    def __init__(self, x: int, y: int, stone: Stone, candidates_added: int):
        self.point: Point =  Point(x, y)
        self.player: Stone = stone
        self.candidates_added: int = candidates_added
        self.took_candidate_place_white: bool = False
        self.took_candidate_place_black: bool = False
    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.point.x == other.point.x and self.point.y == other.point.y and self.player == other.player
    def __str__(self):
        if self.player == 1:
            return f"Point:({self.point.x},{self.point.y}), Player: White"
        return f"Point:({self.point.x},{self.point.y}), Player: Black"
    
class Point:
    "A class simulating a point on a Gomoku board"
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

class CandidateManager:
    """Class that manages the possible points which the minimax should consider"""
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.candidate_points_white = numpy.zeros((board_size, board_size), dtype=bool)
        self.candidate_points_black = numpy.zeros((board_size, board_size), dtype=bool)
        self.candidates_added_white = []
        self.candidates_added_black = []
    
    def deep_copy(self, candidates: list[Candidate]) -> list[Candidate]:
        """Returns a deepcopy of a candidate list"""
        return [Candidate(c.point.x, c.point.y, c.player) for c in candidates]

    def add_candidate_for_player(self, point: Point, player: Stone) -> bool:
        """Add a point to the candidate list of a player"""
        if player == Stone.WHITE:
            self.candidate_points_white[point.y][point.x] = True
            self.candidates_added_white.append(Candidate(point.x, point.y, Stone.WHITE))
            return True
        if player == Stone.BLACK:
            self.candidate_points_black[point.y][point.x] = True
            self.candidates_added_black.append(Candidate(point.x, point.y, Stone.BLACK))
            return True
        return False

    def is_a_candidate(self, point: Point, player: Stone) -> bool:
        """Removes the candidate at some point from one player"""
        if player != Stone.WHITE and player != Stone.BLACK:
            raise Exception('Player error, check if player is handled correctly')
        
        if player == Stone.WHITE:
            if self.candidate_points_white[point.y][point.x] != Stone.EMPTY:
                return True
            return False
        if player == Stone.BLACK:
            if self.candidate_points_black[point.y][point.x] != Stone.EMPTY:
                return True
            return False

    def remove_candidate_from_player(self, point: Point, player: Stone) -> bool:
        """Removes the candidate at some point from one player"""
        if player == Stone.WHITE:
            self.candidate_points_white[point.y][point.x] = False
            for i, candidate in enumerate(self.candidates_added_white):
                if candidate.point.x == point.x and candidate.point.y == point.y:
                    del self.candidates_added_white[i]
                    return True
            return False
        if player == Stone.BLACK:
            self.candidate_points_black[point.y][point.x] = False
            for i, candidate in enumerate(self.candidates_added_black):
                if candidate.point.x == point.x and candidate.point.y == point.y:
                    del self.candidates_added_black[i]
                    return True
            return False

    def clear_all_candidates_at_point(self, point: Point) -> bool:
        """Clears candidates existing in both lists at some point"""
        if self.candidate_points_white[point.y][point.x]:
            self.candidate_points_white[point.y][point.x] = False
        if self.candidate_points_black[point.y][point.x]:
            self.candidate_points_black[point.y][point.x] = False
        self.candidates_added_white = [
            c for c in self.candidates_added_white
            if not (c.point.x == point.x and c.point.y == point.y)
        ]
        self.candidates_added_black = [
            c for c in self.candidates_added_black
            if not (c.point.x == point.x and c.point.y == point.y)
        ]
        return True

