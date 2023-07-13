import pygame
from random import choice
import tkinter as tk
from tkinter import messagebox


class Cell:
    def __init__(self, x, y, thickness):
        self.x, self.y = x, y
        self.thickness = thickness
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self, sc, tile):
        x, y = self.x * tile, self.y * tile
        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('darkgreen'), (x, y), (x + tile, y), self.thickness)
        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('darkgreen'), (x + tile, y), (x + tile, y + tile), self.thickness)
        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('darkgreen'), (x + tile, y + tile), (x , y + tile), self.thickness)
        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('darkgreen'), (x, y + tile), (x, y), self.thickness)

    def check_cell(self, x, y, cols, rows, grid_cells):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbors(self, cols, rows, grid_cells):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1, cols, rows, grid_cells)
        right = self.check_cell(self.x + 1, self.y, cols, rows, grid_cells)
        bottom = self.check_cell(self.x, self.y + 1, cols, rows, grid_cells)
        left = self.check_cell(self.x - 1, self.y, cols, rows, grid_cells)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False


class Maze:
    def __init__(self, cols, rows, start, end):
        self.cols = cols
        self.rows = rows
        self.thickness = 4
        self.grid_cells = [Cell(col, row, self.thickness) for row in range(self.rows) for col in range(self.cols)]
        self.start = start
        self.end = end
        self.grid_cells[start[1] * self.cols + start[0]].walls['left'] = False
        self.grid_cells[end[1] * self.cols + end[0]].walls['right'] = False

    def remove_walls(self, current, next):
        dx = current.x - next.x
        if dx == 1:
            current.walls['left'] = False
            next.walls['right'] = False
        elif dx == -1:
            current.walls['right'] = False
            next.walls['left'] = False
        dy = current.y - next.y
        if dy == 1:
            current.walls['top'] = False
            next.walls['bottom'] = False
        elif dy == -1:
            current.walls['bottom'] = False
            next.walls['top'] = False

    def generate_maze(self):
        current_cell = self.grid_cells[0]
        stack = []
        visited_count = 1
        while visited_count < len(self.grid_cells):
            current_cell.visited = True
            next_cell = current_cell.check_neighbors(self.cols, self.rows, self.grid_cells)
            if next_cell:
                next_cell.visited = True
                visited_count += 1
                stack.append(current_cell)
                self.remove_walls(current_cell, next_cell)
                current_cell = next_cell
            elif stack:
                current_cell = stack.pop()

    def solve_maze(self):
        start_pos = (self.start[0], self.start[1])
        end_pos = (self.end[0], self.end[1])

        queue = [start_pos]
        visited = set()
        parent = {}

        while queue:
            current = queue.pop(0)
            if current == end_pos:
                path = self.reconstruct_path(parent, start_pos, end_pos)
                return path

            visited.add(current)
            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in queue:
                    queue.append(neighbor)
                    parent[neighbor] = current

        return None

    def get_neighbors(self, current):
        x, y = current
        neighbors = [
            (x - 1, y),  # Left
            (x + 1, y),  # Right
            (x, y - 1),  # Up
            (x, y + 1)   # Down
        ]
        return [(nx, ny) for nx, ny in neighbors if self.is_valid_move((x, y), (nx, ny))]

    def is_valid_move(self, current, neighbor):
        current_x, current_y = current
        neighbor_x, neighbor_y = neighbor
        if current_x == neighbor_x:
            if current_y < neighbor_y:
                return not self.grid_cells[current_y * self.cols + current_x].walls['bottom']
            else:
                return not self.grid_cells[current_y * self.cols + current_x].walls['top']
        elif current_y == neighbor_y:
            if current_x < neighbor_x:
                return not self.grid_cells[current_y * self.cols + current_x].walls['right']
            else:
                return not self.grid_cells[current_y * self.cols + current_x].walls['left']
        return False

    def reconstruct_path(self, parent, start, end):
        path = [end]
        current = end
        while current != start:
            current = parent[current]
            path.append(current)
        path.reverse()
        return path

    def draw_path(self, path, tile, thickness, screen):
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            x1_pixel = x1 * tile + tile // 2
            y1_pixel = y1 * tile + tile // 2
            x2_pixel = x2 * tile + tile // 2
            y2_pixel = y2 * tile + tile // 2
            pygame.draw.line(screen, pygame.Color('red'), (x1_pixel, y1_pixel), (x2_pixel, y2_pixel), thickness)


class Player:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.player_size = 10
        self.rect = pygame.Rect(self.x, self.y, self.player_size, self.player_size)
        self.color = (250, 120, 60)
        self.velX = 0
        self.velY = 0
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.speed = 4

    def check_move(self, tile, grid_cells, thickness):
        current_cell_x, current_cell_y = self.x // tile, self.y // tile
        current_cell = self.get_current_cell(current_cell_x, current_cell_y, grid_cells)
        current_cell_abs_x, current_cell_abs_y = current_cell_x * tile, current_cell_y * tile
        if self.left_pressed:
            if current_cell.walls['left']:
                if self.x <= current_cell_abs_x + thickness:
                    self.left_pressed = False
        if self.right_pressed:
            if current_cell.walls['right']:
                if self.x >= current_cell_abs_x + tile - (self.player_size + thickness):
                    self.right_pressed = False
        if self.up_pressed:
            if current_cell.walls['top']:
                if self.y <= current_cell_abs_y + thickness:
                    self.up_pressed = False
        if self.down_pressed:
            if current_cell.walls['bottom']:
                if self.y >= current_cell_abs_y + tile - (self.player_size + thickness):
                    self.down_pressed = False

    def get_current_cell(self, x, y, grid_cells):
        for cell in grid_cells:
            if cell.x == x and cell.y == y:
                return cell

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def update(self):
        self.velX = 0
        self.velY = 0
        if self.left_pressed and not self.right_pressed:
            self.velX = -self.speed
        if self.right_pressed and not self.left_pressed:
            self.velX = self.speed
        if self.up_pressed and not self.down_pressed:
            self.velY = -self.speed
        if self.down_pressed and not self.up_pressed:
            self.velY = self.speed

        self.x += self.velX
        self.y += self.velY

        self.rect = pygame.Rect(int(self.x), int(self.y), self.player_size, self.player_size)


class MenuItem:
    def __init__(self, rect, color, text, font, text_color):
        self.rect = rect
        self.color = color
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


def show_popup_message(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Congratulations", message)
    root.destroy()


def main():
    cols = 50  # Number of columns in the maze
    rows = 30  # Number of rows in the maze
    tile = 30  # Size of each tile in pixels
    start = (0, 0)  # Start position in the maze
    end = (cols - 1, rows - 1)  # End position in the maze

    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption('Maze Game')
    screen_size = (cols * tile, rows * tile)
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()

    # Create the maze and player objects
    maze = Maze(cols, rows, start, end)
    maze.generate_maze()
    player = Player(tile // 3, tile // 3)

    # Create the menu items
    menu_width = 30
    menu_height = 30
    menu_x = 0
    menu_y = 0
    menu_color = pygame.Color(255, 0, 0, 77)
    button_font = pygame.font.Font(None, 20)
    button_text_color = pygame.Color('black')

    solve_button_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height // 2)
    reset_button_rect = pygame.Rect(menu_x, menu_y + menu_height // 2, menu_width, menu_height // 2)
    solve_button_text = 'S'
    reset_button_text = 'R'

    menu_items = [
        MenuItem(solve_button_rect, menu_color, solve_button_text, button_font, button_text_color),
        MenuItem(reset_button_rect, menu_color, reset_button_text, button_font, button_text_color)
    ]

    running = True
    solve_maze = False
    solved_path = []
    while running:
        screen.fill(pygame.Color('white'))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.left_pressed = True
                elif event.key == pygame.K_RIGHT:
                    player.right_pressed = True
                elif event.key == pygame.K_UP:
                    player.up_pressed = True
                elif event.key == pygame.K_DOWN:
                    player.down_pressed = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.left_pressed = False
                elif event.key == pygame.K_RIGHT:
                    player.right_pressed = False
                elif event.key == pygame.K_UP:
                    player.up_pressed = False
                elif event.key == pygame.K_DOWN:
                    player.down_pressed = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for item in menu_items:
                    if item.rect.collidepoint(event.pos):
                        if item.text == solve_button_text:
                            solve_maze = True
                        elif item.text == reset_button_text:
                            maze = Maze(cols, rows, start, end)
                            maze.generate_maze()
                            solved_path = []
                            solve_maze = False

        if solve_maze:
            if not solved_path:
                solved_path = maze.solve_maze()
                if solved_path:
                    show_popup_message('Solved the maze! Click ok to view')
                else:
                    show_popup_message('No solution found for the maze!')

        player.check_move(tile, maze.grid_cells, maze.thickness)
        player.update()

        # Draw maze cells
        for cell in maze.grid_cells:
            cell.draw(screen, tile)

        # Draw start and end points
        pygame.draw.rect(screen, (255, 0, 0), (start[0] * tile, start[1] * tile, tile, tile))
        pygame.draw.rect(screen, (0, 0, 255), (end[0] * tile, end[1] * tile, tile, tile))

        # Draw menu items
        for item in menu_items:
            item.draw(screen)

        if solved_path:
            maze.draw_path(solved_path, tile, maze.thickness, screen)

        # Draw player
        player.draw(screen)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
