from utilities import Candidate, Frame, Move
from stones import Stone
from board import Board


class Minimax:
    """Class that contains the minimax strategy"""
    def __init__(self):
        self.killer_moves = {}

    def run(self, max_depth: int, board: Board) -> tuple[int, Move]:
        """Minimax function that returns a tuple containing the score and the best move"""
        initial_candidates = self.get_candidate(board, board.current_player, depth=0)
        call_stack: list[Frame] = [Frame(0, board.current_player, 0, initial_candidates, None)]
        while call_stack:
            current_frame = call_stack[-1]

            if current_frame.candidate_index > 0:
                board.cancel()

            if current_frame.depth == max_depth:
                if self.handle_max_depth_frame(board, current_frame, call_stack):
                    raise Exception('Please set your the max depth to be greater than or equal to 1')
                
                current_frame = call_stack[-1]
                if current_frame.beta <= current_frame.alpha:
                    self.add_killer_move(current_frame.depth, current_frame.candidates[current_frame.candidate_index - 1])
                    current_frame.candidate_index = len(current_frame.candidates)

                continue

            if current_frame.candidate_index >= len(current_frame.candidates):
                if self.handle_terminal_frame(current_frame, call_stack):
                    return (current_frame.best_score, current_frame.best_candidate)
                
                current_frame = call_stack[-1]
                if current_frame.beta <= current_frame.alpha:
                    self.add_killer_move(current_frame.depth, current_frame.candidates[current_frame.candidate_index - 1])

                continue

            candidate = self.place_next_candidate(board, current_frame)

            next_player = Stone(current_frame.player * -1)

            next_candidates = self.get_candidate(board, next_player, current_frame.depth + 1)

            next_frame = Frame(
                depth=current_frame.depth + 1,
                player=next_player,
                candidate_index=0,
                candidates=next_candidates,
                current_candidate= Candidate(candidate.point.x, candidate.point.y, candidate.player),
                alpha = current_frame.alpha,
                beta = current_frame.beta
            )
            self.add_new_frame(next_frame, call_stack)

    def handle_terminal_frame(self, frame: Frame, call_stack: list[Frame]) -> bool:
        """Handles the case when we traversed all candidates of a frame, returns true if there exists no more frames and we are done"""
        if frame.candidate_index >= len(frame.candidates):
            best_score = frame.best_score

            call_stack.pop()

            if not call_stack:
                return True
            
            parent_frame = call_stack[-1]

            if parent_frame.player == Stone.WHITE:
                if best_score > parent_frame.best_score:
                    parent_frame.best_score = best_score
                    parent_frame.best_candidate = Candidate(frame.current_candidate.point.x, frame.current_candidate.point.y, frame.current_candidate.player)
                
                if best_score > parent_frame.alpha:
                    parent_frame.alpha = best_score
                    


            if parent_frame.player == Stone.BLACK:
                if best_score < parent_frame.best_score:
                    parent_frame.best_score = best_score
                    parent_frame.best_candidate = Candidate(frame.current_candidate.point.x, frame.current_candidate.point.y, frame.current_candidate.player)
                
                if best_score < parent_frame.beta:
                    parent_frame.beta = best_score
                    

            return False
        
    def handle_max_depth_frame(self, board: Board, frame: Frame, call_stack: list[Frame]) -> bool:
        """Handles the case when we reached maximum recursion depth, returns true if there are no more frames and we are done"""
        score = board.evaluate_board()

        call_stack.pop()

        if not call_stack:
            return True
        
        parent_frame = call_stack[-1]

        if parent_frame.player == Stone.WHITE:
            if score > parent_frame.best_score:
                parent_frame.best_score = score
                parent_frame.best_candidate = Candidate(frame.current_candidate.point.x, frame.current_candidate.point.y, frame.current_candidate.player)
            
            if score > parent_frame.alpha:
                parent_frame.alpha = score
                return False

        if parent_frame.player == Stone.BLACK:
            if score < parent_frame.best_score:
                parent_frame.best_score = score
                parent_frame.best_candidate = Candidate(frame.current_candidate.point.x, frame.current_candidate.point.y, frame.current_candidate.player)

            if score < parent_frame.beta:
                parent_frame.beta = score
                return False

        return False
    
    def place_next_candidate(self, board: Board, frame: Frame) -> Candidate:
        """Places the current candidate for the current frame on the board, returns the candidate being placed"""
        candidate = frame.candidates[frame.candidate_index]

        frame.candidate_index += 1

        board.place(candidate.point.x, candidate.point.y)

        return candidate

    def add_new_frame(self, frame: Frame, call_stack: list[Frame]):
        """Appends the frame onto the call stack"""
        call_stack.append(frame)


    def add_killer_move(self, depth: int, move: Candidate):
        """Adds a killer move for the given depth"""
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        
        if move not in self.killer_moves[depth]:
            if len(self.killer_moves[depth]) >= 3:
                self.killer_moves[depth].pop()
            
            self.killer_moves[depth].insert(0, move)
    
    def get_candidate(self, board: Board, player: Stone, depth: int):
        """Returns a deepcopy of the candidates of the player entered, with killer moves prioritized"""
        current_score = board.evaluate_board()
    
        if current_score >= 1000:
            candidates = board.candidates_manager.deep_copy(board.candidates_manager.candidates_added_white)
        elif current_score <= -1000:
            candidates = board.candidates_manager.deep_copy(board.candidates_manager.candidates_added_black)
        elif player == Stone.WHITE:
            if not board.candidates_manager.candidates_added_white:
                candidates = board.candidates_manager.deep_copy(board.candidates_manager.candidates_added_black)
            else:
                candidates = board.candidates_manager.deep_copy(board.candidates_manager.candidates_added_white)
        else:  # player == Stone.BLACK
            if not board.candidates_manager.candidates_added_black:
                candidates = board.candidates_manager.deep_copy(board.candidates_manager.candidates_added_white)
            else:
                candidates = board.candidates_manager.deep_copy(board.candidates_manager.candidates_added_black)
    
        if depth is not None and depth in self.killer_moves:
            killer_moves = self.killer_moves[depth]
             
            for move in killer_moves:
                if move in candidates:
                    candidates.remove(move)
                    candidates.insert(0, move)
        
        return candidates