import tkinter as tk
from tkinter import messagebox
import os

try:
    import pygame
    pygame.mixer.init()
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

# Налаштування гри
GRID_SIZE = 10
CELL_SIZE = 50 
SHIPS_TO_PLACE = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1] 
TOTAL_SHIP_CELLS = sum(SHIPS_TO_PLACE)

# Кольори 
COLOR_WATER = "#d3d3d3"       
COLOR_ENEMY_WATER = "#d3d3d3" 
COLOR_SHIP = "#555555"        

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Морський Бій - Головне Меню")
        
        self.root.geometry("1200x800")
        
        self.frame = tk.Frame(root)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(self.frame, text="МОРСЬКИЙ БІЙ\n(Гарячий стілець)", font=("Arial", 32, "bold"), fg="navy")
        title.pack(pady=30)

        play_btn = tk.Button(self.frame, text="Грати", font=("Arial", 18, "bold"), width=15, height=2, bg="lightgreen", command=self.start_game)
        play_btn.pack(pady=15)

        exit_btn = tk.Button(self.frame, text="Вихід", font=("Arial", 18, "bold"), width=15, height=2, bg="salmon", command=self.root.destroy)
        exit_btn.pack(pady=15)

    def start_game(self):
        self.frame.destroy()
        BattleshipGame(self.root)


class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Морський Бій - Бій!")
        self.root_bg = self.root.cget("bg") 
        
        self.game_state = "P1_SETUP" 
        self.transition_next_state = ""
        self.status_msg = "" 
        
        self.horizontal_placement = True
        self.current_ship_idx = 0
        
        self.p1_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.p2_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        self.p1_ships = [] 
        self.p2_ships = []
        
        self.p1_hits = 0 
        self.p2_hits = 0 

        self.images = {
            "water": self.load_image("water.png"), "ship": self.load_image("ship.png"),
            "hit": self.load_image("hit.png"), "miss": self.load_image("miss.png")
        }
        
        self.trans_frame = tk.Frame(root)
        self.trans_label = tk.Label(self.trans_frame, text="", font=("Arial", 24, "bold"))
        self.trans_label.pack(pady=40)
        self.trans_btn = tk.Button(self.trans_frame, text="Я готовий!", font=("Arial", 18, "bold"), bg="lightyellow", width=15, height=2, command=self.end_transition)
        self.trans_btn.pack(pady=10)

        self.center_frame = tk.Frame(root)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.info_label = tk.Label(self.center_frame, text="", font=("Arial", 22, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.p1_canvas = tk.Canvas(self.center_frame, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg=COLOR_WATER, highlightthickness=5)
        self.p1_canvas.grid(row=1, column=0, padx=50)
        self.p1_canvas.bind("<Button-1>", self.left_canvas_click)
        self.p1_canvas.bind("<Button-3>", self.rotate_ship)
        
        self.p2_canvas = tk.Canvas(self.center_frame, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg=COLOR_ENEMY_WATER, highlightthickness=5)
        self.p2_canvas.grid(row=1, column=1, padx=50)
        self.p2_canvas.bind("<Button-1>", self.right_canvas_click)
        self.p2_canvas.bind("<Button-3>", self.rotate_ship)

        self.lbl_field1 = tk.Label(self.center_frame, text="Поле кораблів синього гравця", font=("Arial", 18, "bold"), fg="blue")
        self.lbl_field1.grid(row=2, column=0, pady=(15, 0))
        
        self.lbl_field2 = tk.Label(self.center_frame, text="Поле кораблів червоного гравця ", font=("Arial", 18, "bold"), fg="red")
        self.lbl_field2.grid(row=2, column=1, pady=(15, 0))

        self.controls_label = tk.Label(self.center_frame, text="", font=("Arial", 16, "bold"), fg="#444444")
        self.controls_label.grid(row=3, column=0, columnspan=2, pady=(30, 0))

        self.update_ui()

    def load_image(self, filename):
        return tk.PhotoImage(file=filename) if os.path.exists(filename) else None

    def show_transition(self, message, next_state):
        self.game_state = "TRANSITION"
        self.transition_next_state = next_state
        self.center_frame.place_forget() 
        self.trans_frame.place(relx=0.5, rely=0.5, anchor="center") 
        self.trans_label.config(text=message)

    def end_transition(self):
        self.game_state = self.transition_next_state
        self.trans_frame.place_forget()
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.update_ui()

    def update_ui(self):
        orientation = "Горизонтально" if self.horizontal_placement else "Вертикально"
        
        if self.game_state == "P1_SETUP":
            self.info_label.config(text=f"СИНІЙ гравець розставляє: {SHIPS_TO_PLACE[self.current_ship_idx]} палуб ({orientation})", fg="blue")
            self.p1_canvas.config(highlightbackground="black", highlightcolor="black")
            self.p2_canvas.config(highlightbackground=self.root_bg, highlightcolor=self.root_bg)
            
        elif self.game_state == "P2_SETUP":
            self.info_label.config(text=f"ЧЕРВОНИЙ гравець розставляє: {SHIPS_TO_PLACE[self.current_ship_idx]} палуб ({orientation})", fg="red")
            self.p1_canvas.config(highlightbackground=self.root_bg, highlightcolor=self.root_bg)
            self.p2_canvas.config(highlightbackground="black", highlightcolor="black")
            
        elif self.game_state == "BATTLE_P1_TURN":
            self.info_label.config(text=f"{self.status_msg}Хід СИНЬОГО гравця", fg="blue")
            self.p1_canvas.config(highlightbackground=self.root_bg, highlightcolor=self.root_bg)
            self.p2_canvas.config(highlightbackground="black", highlightcolor="black")
            
        elif self.game_state == "BATTLE_P2_TURN":
            self.info_label.config(text=f"{self.status_msg}Хід ЧЕРВОНОГО гравця", fg="red")
            self.p1_canvas.config(highlightbackground="black", highlightcolor="black")
            self.p2_canvas.config(highlightbackground=self.root_bg, highlightcolor=self.root_bg)

        if self.game_state in ["P1_SETUP", "P2_SETUP"]:
            self.controls_label.config(text="ЛКМ (Ліва кнопка) - поставити корабель   |   ПКМ (Права кнопка) - змінити орієнтацію")
        else:
            self.controls_label.config(text="ЛКМ (Ліва кнопка) - постріл")

        self.draw_grids()

    def draw_grids(self):
        self.p1_canvas.delete("all")
        self.p2_canvas.delete("all")
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                val1 = self.p1_grid[r][c]
                val2 = self.p2_grid[r][c]

                if self.game_state in ["BATTLE_P1_TURN", "BATTLE_P2_TURN"]:
                    display1 = 0 if val1 == 1 else val1
                    display2 = 0 if val2 == 1 else val2
                elif self.game_state == "P2_SETUP":
                    display1 = 0 if val1 == 1 else val1
                    display2 = val2
                else: 
                    display1 = val1
                    display2 = 0 if val2 == 1 else val2

                # Відмальовуємо клітинки, передаючи колір для влучання (синій для лівого поля, червоний для правого)
                self.draw_cell(self.p1_canvas, display1, x1, y1, x2, y2, COLOR_WATER, hit_color="blue")
                self.draw_cell(self.p2_canvas, display2, x1, y1, x2, y2, COLOR_ENEMY_WATER, hit_color="red")

    def draw_cell(self, canvas, val, x1, y1, x2, y2, default_bg, hit_color):
        if self.images["water"]: canvas.create_image(x1, y1, anchor=tk.NW, image=self.images["water"])
        else: canvas.create_rectangle(x1, y1, x2, y2, fill=default_bg, outline="#aaaaaa")

        if val == 1:
            if self.images["ship"]: canvas.create_image(x1, y1, anchor=tk.NW, image=self.images["ship"])
            else: canvas.create_rectangle(x1, y1, x2, y2, fill=COLOR_SHIP, outline="black")
        elif val == 2:
            if self.images["hit"]: canvas.create_image(x1, y1, anchor=tk.NW, image=self.images["hit"])
            else: 
                # Повністю зафарбовуємо клітинку при влучанні відповідним кольором (синім або червоним)
                canvas.create_rectangle(x1, y1, x2, y2, fill=hit_color, outline="#aaaaaa")
        elif val == 3:
            if self.images["miss"]: canvas.create_image(x1, y1, anchor=tk.NW, image=self.images["miss"])
            else: 
                # Повністю зафарбовуємо клітинку білим кольором при промаху
                canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="#aaaaaa")

    def rotate_ship(self, event):
        if self.game_state in ["P1_SETUP", "P2_SETUP"]:
            self.horizontal_placement = not self.horizontal_placement
            self.update_ui()

    def can_place_ship(self, grid, r, c, length, horizontal):
        if horizontal and c + length > GRID_SIZE: return False
        if not horizontal and r + length > GRID_SIZE: return False
        for i in range(length):
            cur_r = r if horizontal else r + i
            cur_c = c + i if horizontal else c
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = cur_r + dr, cur_c + dc
                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                        if grid[nr][nc] == 1: return False
        return True

    def place_ship(self, grid, r, c, length, horizontal, ships_list):
        ship_coords = []
        for i in range(length):
            cur_r = r if horizontal else r + i
            cur_c = c + i if horizontal else c
            grid[cur_r][cur_c] = 1
            ship_coords.append((cur_r, cur_c))
        ships_list.append(ship_coords)

    def check_sunk(self, grid, ships_list, hit_r, hit_c):
        hit_ship = None
        for ship in ships_list:
            if (hit_r, hit_c) in ship:
                hit_ship = ship
                break
        
        if hit_ship:
            is_sunk = all(grid[r][c] == 2 for r, c in hit_ship)
            if is_sunk:
                for r, c in hit_ship:
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                                if grid[nr][nc] == 0: 
                                    grid[nr][nc] = 3
                return True
        return False

    def left_canvas_click(self, event):
        c, r = event.x // CELL_SIZE, event.y // CELL_SIZE
        
        if self.game_state == "P1_SETUP":
            ship_len = SHIPS_TO_PLACE[self.current_ship_idx]
            if self.can_place_ship(self.p1_grid, r, c, ship_len, self.horizontal_placement):
                self.place_ship(self.p1_grid, r, c, ship_len, self.horizontal_placement, self.p1_ships)
                self.current_ship_idx += 1
                
                if self.current_ship_idx >= len(SHIPS_TO_PLACE):
                    self.current_ship_idx = 0 
                    self.show_transition("СИНІЙ гравець розставив кораблі!\n\nВідверніться і передайте пристрій ЧЕРВОНОМУ гравцю.", "P2_SETUP")
                else:
                    self.update_ui()

        elif self.game_state == "BATTLE_P2_TURN":
            if self.p1_grid[r][c] in [2, 3]: return 
            
            if self.p1_grid[r][c] == 1:
                self.p1_grid[r][c] = 2
                self.p2_hits += 1
                
                if self.check_sunk(self.p1_grid, self.p1_ships, r, c):
                    self.status_msg = "🔥 ПОТОПЛЕНО! Стріляйте ще. | "
                else:
                    self.status_msg = "💥 ВЛУЧИВ! Стріляйте ще. | "
            else:
                self.p1_grid[r][c] = 3
                self.status_msg = "💦 МИМО. | "
                self.game_state = "BATTLE_P1_TURN"
                
            self.update_ui()
            
            if self.p2_hits == TOTAL_SHIP_CELLS:
                messagebox.showinfo("Перемога!", "ЧЕРВОНИЙ гравець знищив всі кораблі і виграв!")
                self.root.destroy()

    def right_canvas_click(self, event):
        c, r = event.x // CELL_SIZE, event.y // CELL_SIZE
        
        if self.game_state == "P2_SETUP":
            ship_len = SHIPS_TO_PLACE[self.current_ship_idx]
            if self.can_place_ship(self.p2_grid, r, c, ship_len, self.horizontal_placement):
                self.place_ship(self.p2_grid, r, c, ship_len, self.horizontal_placement, self.p2_ships)
                self.current_ship_idx += 1
                
                if self.current_ship_idx >= len(SHIPS_TO_PLACE):
                    self.status_msg = "Бій розпочато! | "
                    self.show_transition("ЧЕРВОНИЙ гравець розставив кораблі!\n\nБІЙ ПОЧИНАЄТЬСЯ!", "BATTLE_P1_TURN")
                else:
                    self.update_ui()

        elif self.game_state == "BATTLE_P1_TURN":
            if self.p2_grid[r][c] in [2, 3]: return 
            
            if self.p2_grid[r][c] == 1:
                self.p2_grid[r][c] = 2
                self.p1_hits += 1
                
                if self.check_sunk(self.p2_grid, self.p2_ships, r, c):
                    self.status_msg = "🔥 ПОТОПЛЕНО! Стріляйте ще. | "
                else:
                    self.status_msg = "💥 ВЛУЧИВ! Стріляйте ще. | "
            else:
                self.p2_grid[r][c] = 3
                self.status_msg = "💦 МИМО. | "
                self.game_state = "BATTLE_P2_TURN" 
                
            self.update_ui()
            
            if self.p1_hits == TOTAL_SHIP_CELLS:
                messagebox.showinfo("Перемога!", "СИНІЙ гравець знищив всі кораблі і виграв!")
                self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root) 
    root.mainloop()