import tkinter as tk
from tkinter import messagebox
import math
from ctypes import windll
from board import Point
from utilities import Candidate
from board import Board
from stones import Stone
from board import Move
from timer import Timer
import cProfile
from bot import Bot
import threading
import time
import pstats
import io


def distance(point_one: tuple[float, float], point_two: tuple[float, float]):
    x_component = point_one[0] - point_two[0]
    y_component = point_one[1] - point_two[1]
    return x_component * x_component + y_component * y_component

class UI:
    def __init__(self, board: Board, bot: Bot = None):
        self.bot = bot
        self.board = board
        self.current_player = Stone.WHITE
        self.board_size = (self.board).board_size
        self.font_size = 18 #default
        self.cell_size = 75
        self.stone_radius = 20

        self.root = tk.Tk()
        windll.shcore.SetProcessDpiAwareness(1)
        self.root.title("Gomoku")
        self.root.geometry("1300x1300") 
        self.canvas = tk.Canvas(self.root, width=(self.board_size+1)*self.cell_size, height=(self.board_size+1)*self.cell_size, bg="#F5DEB3")
        self.canvas.pack(fill=tk.BOTH, expand=True) 

        self.draw_board(self.canvas)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<KeyPress-m>", self.on_key_m)
        self.canvas.bind("<KeyPress-l>", self.on_key_l)
        self.canvas.bind("<KeyPress-p>", self.on_key_p)
        self.canvas.focus_set()

        self.root.mainloop()

    def draw_board(self, canvas: tk.Canvas) -> None:
        for i in range(self.board_size):
            canvas.create_line(self.cell_size, self.cell_size*(i+1), self.cell_size*self.board_size, self.cell_size*(i+1), tags='grid')
            canvas.create_line(self.cell_size*(i+1), self.cell_size, self.cell_size*(i+1), self.cell_size*(self.board_size), tags='grid')
        
    def mouse_move(self, event) -> None:
        mouse_x = (event.x / self.cell_size)-1
        mouse_y = (event.y / self.cell_size)-1
        closest_neighbor = self.get_closest_neighbor_of_mouse(mouse_x, mouse_y)
        if not closest_neighbor:
            self.canvas.delete("coord_display")
            self.coord_text_id = None
            return

        if closest_neighbor.x < 0 or closest_neighbor.x >= self.board_size:
            self.canvas.delete("coord_display")
            self.coord_text_id = None
            return
        
        if closest_neighbor.y < 0 or closest_neighbor.y >= self.board_size:
            self.canvas.delete("coord_display")
            self.coord_text_id = None
            return

        text = f"({closest_neighbor.x}, {closest_neighbor.y})"
        if self.coord_text_id:
            # Update existing
            self.canvas.coords(self.coord_text_id, event.x + 25, event.y + 25)
            self.canvas.itemconfig(self.coord_text_id, text=text, font=("Arial", self.font_size, "bold"))
        else:
            # Create first time
            self.coord_text_id = self.canvas.create_text(
                event.x + 25, event.y + 25,
                text=text, fill="#C33149", 
                font= ("Arial", self.font_size, "bold"), 
                anchor="nw",
                tag="coord_display"
                )

    def get_closest_neighbor_of_mouse(self, x: float, y: float) -> Point:
        current_mouse_position = (x, y)
        floor_x = math.floor(x)
        floor_y = math.floor(y)

        ceil_x =  math.ceil(x)
        ceil_y = math.ceil(y)

        neighbors = [
            (floor_x, floor_y),
            (floor_x, ceil_y),
            (ceil_x, floor_y),
            (ceil_x, ceil_y)
        ]
        distances = [distance(current_mouse_position, neighbor) for neighbor in neighbors]

        distance_to_closest_neighbor = min(distances)
        if distance_to_closest_neighbor <= 0.2:
            index = distances.index(distance_to_closest_neighbor)
            return Point(neighbors[index][0], neighbors[index][1])
        else:
            return
        
    def on_click(self, event) -> None:
        mouse_x = (event.x / self.cell_size)-1
        mouse_y = (event.y / self.cell_size)-1
        closest_neighbor = self.get_closest_neighbor_of_mouse(mouse_x, mouse_y)

        if not closest_neighbor:
            return

        if closest_neighbor.x < 0 or closest_neighbor.x >= self.board_size:
            return
        
        if closest_neighbor.y < 0 or closest_neighbor.y >= self.board_size:
            return
        
        self.board.place(closest_neighbor.x, closest_neighbor.y)
        self.draw_stones(self.canvas, self.board.move_stack[-1])
        if self.board.check_win(closest_neighbor.x, closest_neighbor.y, self.board.move_stack[-1].player):
            winner = "Black" if self.board.move_stack[-1].player == Stone.BLACK else "White"
            answer = messagebox.askyesno("Game Over", f"{winner} Won！\nDo you want to play again?")
            self.canvas.unbind("<Button-1>")
            if answer:
                self.board.reset()
                self.canvas.delete("all")
                self.draw_board(self.canvas)
                self.canvas.bind("<Button-1>", self.on_click)
            else:
                self.root.destroy()
            return
        
        if self.bot != None:
            self.canvas.unbind("<Button-1>")
            threading.Thread(target=self.trigger_ai_turn, daemon=True).start()
            
        
    def redraw_board(self, canvas: tk.Canvas) -> None:
        canvas.delete("stones")
        for move in self.board.move_stack:
            self.draw_stones(canvas, move)

    def draw_stones(self, canvas: tk.Canvas, move: Move) -> None:
        x = (move.point.x + 1) * self.cell_size
        y = (move.point.y + 1) * self.cell_size
        if move.player == Stone.WHITE:
            color = 'white'
        else:
            color = 'black'
        canvas.create_oval(x-self.stone_radius, y-self.stone_radius, x+self.stone_radius, y+self.stone_radius, fill=color, tags='stones')

    def draw_candidate_stone(self, canvas: tk.Canvas, candidate: Candidate, specify_color: str = None) -> None:
        x = (candidate.point.x + 1) * self.cell_size
        y = (candidate.point.y + 1) * self.cell_size

        if specify_color != None:
            canvas.create_oval(x-self.stone_radius, y-self.stone_radius, x+self.stone_radius, y+self.stone_radius, fill=specify_color, tags='stones')
            return

        if candidate.player == Stone.WHITE:
            color = '#ADD8E6'
        else:
            color = "#F08080"
        canvas.create_oval(x-self.stone_radius, y-self.stone_radius, x+self.stone_radius, y+self.stone_radius, fill=color, tags='stones')
    
    def on_canvas_resize(self, event):
        new_width = event.width
        new_height = event.height
        size = min(new_width, new_height)
        self.cell_size = size / (self.board_size + 1)
        self.stone_radius = self.cell_size * 0.35 
        self.canvas.delete("all") 

        self.coord_text_id = None
        self.font_size = math.ceil(self.stone_radius*0.7)
        self.draw_board(self.canvas)
        print(self.board.move_stack)
        for move in self.board.move_stack:
            self.draw_stones(self.canvas, move)
    
    def draw_candidates(self, canvas:tk.Canvas):
        for candidate in self.board.candidates_manager.candidates_added_white:
            self.draw_candidate_stone(canvas, candidate)

        for candidate in self.board.candidates_manager.candidates_added_black:
            self.draw_candidate_stone(canvas, candidate)
    
    def trigger_ai_turn(self):
        start = time.time()
        pr = cProfile.Profile()
        pr.enable()

        

        (score, ai_move) = self.bot.minimax.run(max_depth=3, board=self.board)


        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
        ps.print_stats(20)  # 显示前 20 个函数
        print(s.getvalue())

        elapsed = time.time() - start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

        def place_ai_move():
            self.board.place(ai_move.point.x, ai_move.point.y)
            self.draw_stones(self.canvas, self.board.move_stack[-1])

            if self.board.check_win(ai_move.point.x, ai_move.point.y, self.board.move_stack[-1].player):
                winner = "Black" if self.board.move_stack[-1].player == Stone.BLACK else "White"
                answer = messagebox.askyesno("Game Over", f"{winner} Won!\nDo you want to play again?")
                self.canvas.unbind("<Button-1>")
                if answer:
                    self.board.reset()
                    self.canvas.delete("all")
                    self.draw_board(self.canvas)
                    self.canvas.bind("<Button-1>", self.on_click)
                else:
                    self.root.destroy()
            else:
                self.canvas.bind("<Button-1>", self.on_click)
        self.root.after(0, place_ai_move)

    def on_key_m(self):
        with Timer('Minimax'):
            print(self.bot.minimax.run(max_depth=3, board=self.board))

    def on_key_l(self):
        with Timer('Cancel'):
            self.board.cancel()
            self.redraw_board(self.canvas)

    def on_key_p(self):
        self.draw_candidates(self.canvas)

    