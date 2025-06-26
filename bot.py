from utilities import Candidate, Frame
from stones import Stone
from board import Board


class Bot:
    def minimax_iterative(self, max_depth: int, board: Board) -> int:
            if board.current_player == Stone.WHITE:
                initial_candidates = board.candidates_manager.deep_copy_candidates(board.candidates_manager.candidates_added_white)
            else:
                initial_candidates = board.candidates_manager.deep_copy_candidates(board.candidates_manager.candidates_added_black) 
            
            # if not initial_candidates:
            #     initial_candidates = [Candidate(board.move_stack[-1].point.x+1, board.move_stack[-1].point.y, Stone.BLACK)]
                
            call_stack: list[Frame] = [Frame(0, board.current_player, 0, initial_candidates, None)]
            while call_stack:
                current_frame = call_stack[-1]

                if current_frame.candidate_index > 0:
                    board.cancel()

                if current_frame.depth == max_depth:
                    score = board.evaluate_board()
                    call_stack.pop()
                    if not call_stack:
                        return score
                    
                    parent_frame = call_stack[-1]
                    if parent_frame.player == Stone.WHITE and score > parent_frame.best_score:
                        parent_frame.best_score = score
                        parent_frame.best_candidate = Candidate(current_frame.current_candidate.point.x, current_frame.current_candidate.point.y, current_frame.current_candidate.player)

                    if parent_frame.player == Stone.BLACK and score < parent_frame.best_score:
                        parent_frame.best_score = score
                        parent_frame.best_candidate = Candidate(current_frame.current_candidate.point.x, current_frame.current_candidate.point.y, current_frame.current_candidate.player)


                    continue

                if current_frame.candidate_index >= len(current_frame.candidates):
                    best_score = current_frame.best_score
                    best_move = current_frame.best_candidate

                    call_stack.pop()

                    if not call_stack:
                        return (best_score, best_move)
                    
                    parent_frame = call_stack[-1]

                    if parent_frame.player == Stone.WHITE and best_score > parent_frame.best_score:
                        parent_frame.best_score = best_score
                        parent_frame.best_candidate = Candidate(current_frame.current_candidate.point.x, current_frame.current_candidate.point.y, current_frame.current_candidate.player)

                    if parent_frame.player == Stone.BLACK and best_score < parent_frame.best_score:
                        parent_frame.best_score = best_score
                        parent_frame.best_candidate = Candidate(current_frame.current_candidate.point.x, current_frame.current_candidate.point.y, current_frame.current_candidate.player)


                    continue

                candidate = current_frame.candidates[current_frame.candidate_index]
                current_frame.candidate_index += 1
                board.place(candidate.point.x, candidate.point.y)
        
                
                next_player = Stone(current_frame.player * -1)
                if next_player == Stone.WHITE:
                    next_candidates = board.candidates_manager.deep_copy_candidates(board.candidates_manager.candidates_added_white) 
                else:
                    next_candidates = board.candidates_manager.deep_copy_candidates(board.candidates_manager.candidates_added_black) 
                
                call_stack.append(Frame(
                    depth=current_frame.depth + 1,
                    player=next_player,
                    candidate_index=0,
                    candidates=next_candidates,
                    current_candidate= Candidate(candidate.point.x, candidate.point.y, candidate.player)
                ))
                