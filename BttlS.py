import tkinter as tk
from tkinter import messagebox
import random

# Налаштування гри
GRID_SIZE = 10
CELL_SIZE = 30
SHIPS_TO_PLACE = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1] # 1х4, 2х3, 3х2, 4х1
TOTAL_SHIP_CELLS = sum(SHIPS_TO_PLACE)

# Кольори
COLOR_WATER = "lightblue"
COLOR_SHIP = "gray"
COLOR_HIT = "red"
COLOR_MISS = "white"
COLOR_ENEMY_WATER = "blue"

class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Морський Бій")
        
        self.setup_phase = True
        self.horizontal_placement = True
        self.current_ship_idx = 0
        
        # Матриці полів: 0 - вода, 1 - корабель, 2 - влучання, 3 - промах
        self.player_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.enemy_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        self.player_hits = 0
        self.enemy_hits = 0
        
        # Інтерфейс
        self.info_label = tk.Label(root, text="Розставте свої кораблі. Права кнопка - повернути корабель.", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.player_canvas = tk.Canvas(root, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg=COLOR_WATER)
        self.player_canvas.grid(row=1, column=0, padx=20, pady=20)
        self.player_canvas.bind("<Button-1>", self.player_click)
        self.player_canvas.bind("<Button-3>", self.rotate_ship) # Права кнопка миші для обертання
        
        self.enemy_canvas = tk.Canvas(root, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg=COLOR_ENEMY_WATER)
        self.enemy_canvas.grid(row=1, column=1, padx=20, pady=20)
        self.enemy_canvas.bind("<Button-1>", self.enemy_click)
        
        self.draw_grids()
        
    def draw_grids(self):
        self.player_canvas.delete("all")
        self.enemy_canvas.delete("all")
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Малювання поля гравця
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                p_val = self.player_grid[r][c]
                color = COLOR_WATER
                if p_val == 1: color = COLOR_SHIP
                elif p_val == 2: color = COLOR_HIT
                elif p_val == 3: color = COLOR_MISS
                self.player_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Малювання поля ворога (кораблі приховані)
                e_val = self.enemy_grid[r][c]
                e_color = COLOR_ENEMY_WATER
                if e_val == 2: e_color = COLOR_HIT
                elif e_val == 3: e_color = COLOR_MISS
                self.enemy_canvas.create_rectangle(x1, y1, x2, y2, fill=e_color, outline="black")

    def rotate_ship(self, event):
        if self.setup_phase:
            self.horizontal_placement = not self.horizontal_placement
            orientation = "Горизонтально" if self.horizontal_placement else "Вертикально"
            self.info_label.config(text=f"Розміщення корабля довжиною {SHIPS_TO_PLACE[self.current_ship_idx]} ({orientation})")

    def can_place_ship(self, grid, r, c, length, horizontal):
        # Перевірка виходу за межі
        if horizontal and c + length > GRID_SIZE: return False
        if not horizontal and r + length > GRID_SIZE: return False
        
        # Перевірка накладання та сусідніх клітинок (правило 1 клітинки відстані)
        for i in range(length):
            cur_r = r if horizontal else r + i
            cur_c = c + i if horizontal else c
            
            # Перевірка квадрата 3х3 навколо кожної палуби корабля
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = cur_r + dr, cur_c + dc
                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                        if grid[nr][nc] == 1:
                            return False
        return True

    def place_ship(self, grid, r, c, length, horizontal):
        for i in range(length):
            if horizontal:
                grid[r][c+i] = 1
            else:
                grid[r+i][c] = 1

    def player_click(self, event):
        if not self.setup_phase: return
        
        c, r = event.x // CELL_SIZE, event.y // CELL_SIZE
        ship_len = SHIPS_TO_PLACE[self.current_ship_idx]
        
        if self.can_place_ship(self.player_grid, r, c, ship_len, self.horizontal_placement):
            self.place_ship(self.player_grid, r, c, ship_len, self.horizontal_placement)
            self.current_ship_idx += 1
            self.draw_grids()
            
            if self.current_ship_idx >= len(SHIPS_TO_PLACE):
                self.setup_phase = False
                self.place_enemy_ships()
                self.info_label.config(text="Бій почався! Стріляйте по правому полю.", fg="red")
            else:
                orientation = "Горизонтально" if self.horizontal_placement else "Вертикально"
                self.info_label.config(text=f"Розміщення корабля довжиною {SHIPS_TO_PLACE[self.current_ship_idx]} ({orientation})")

    def place_enemy_ships(self):
        for length in SHIPS_TO_PLACE:
            placed = False
            while not placed:
                r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
                horiz = random.choice([True, False])
                if self.can_place_ship(self.enemy_grid, r, c, length, horiz):
                    self.place_ship(self.enemy_grid, r, c, length, horiz)
                    placed = True

    def enemy_click(self, event):
        if self.setup_phase: return
        
        c, r = event.x // CELL_SIZE, event.y // CELL_SIZE
        
        if self.enemy_grid[r][c] in [2, 3]: # Вже стріляли сюди
            return
            
        if self.enemy_grid[r][c] == 1:
            self.enemy_grid[r][c] = 2
            self.player_hits += 1
        else:
            self.enemy_grid[r][c] = 3
            
        self.draw_grids()
        
        if self.player_hits == TOTAL_SHIP_CELLS:
            messagebox.showinfo("Перемога!", "Ви знищили всі кораблі ворога!")
            self.root.destroy()
            return
            
        # Хід комп'ютера (після пострілу гравця)
        self.computer_turn()

    def computer_turn(self):
        # Простий AI: стріляє випадково в пусті клітинки
        while True:
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if self.player_grid[r][c] not in [2, 3]:
                if self.player_grid[r][c] == 1:
                    self.player_grid[r][c] = 2
                    self.enemy_hits += 1
                else:
                    self.player_grid[r][c] = 3
                break
                
        self.draw_grids()
        
        if self.enemy_hits == TOTAL_SHIP_CELLS:
            messagebox.showinfo("Поразка", "Комп'ютер знищив всі ваші кораблі!")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = BattleshipGame(root)
    root.mainloop()