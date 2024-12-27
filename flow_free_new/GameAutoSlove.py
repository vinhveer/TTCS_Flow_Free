from typing import List, Tuple, Optional, Dict, Set
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from collections import deque
import copy

from GridData import GridData
from GameRender import GameRenderer

class GameController:
    """
    Manages game logic for path generation and visualization.
    Includes enhanced solving capabilities with complete board filling.
    """

    def __init__(self, grid_size: int = 10, window_size: int = 800):
        self.grid_data = GridData()
        self.grid_size = self.grid_data.getSize()
        self.cell_size = (window_size - 100) // self.grid_size

        self.endpoints: List[Tuple[int, int, int]] = []
        self.completed_paths: List[Tuple[List[Tuple[int, int]], int]] = []
        self.current_path: List[Tuple[int, int]] = []
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.is_drawing = False
        self.solution_paths = []

        self.renderer = GameRenderer(self)
        self._reset_game_state()

    def _reset_game_state(self) -> None:
        """Reset all game state variables to initial conditions."""
        self.endpoints.clear()
        self.completed_paths.clear()
        self.current_path.clear()
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.is_drawing = False
        self.solution_paths = []
        self._collect_endpoints()

    def _collect_endpoints(self) -> None:
        """Identify and store color endpoints across the grid."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color_number = self.grid_data.get_color_point(row, col)
                if color_number > 0:
                    self.endpoints.append((row, col, color_number))

    def visualize_paths(self) -> None:
        """Initiate comprehensive path visualization for all colors."""
        self._reset_game_state()
        colors_to_visualize = list(set(endpoint[2] for endpoint in self.endpoints))
        if colors_to_visualize:
            self._visualize_color_paths(colors_to_visualize)
        else:
            self._show_message("No Paths", "No endpoints found to visualize.")

    def _visualize_color_paths(self, colors: List[int]) -> None:
        """Visualize paths for given colors sequentially."""
        if not colors:
            self._show_victory_message()
            return

        current_color = colors[0]
        color_endpoints = [point for point in self.endpoints if point[2] == current_color]

        if len(color_endpoints) != 2:
            self._visualize_color_paths(colors[1:])
            return

        start, end = color_endpoints[0][:2], color_endpoints[1][:2]
        self.current_color = str(current_color)
        self.current_color_number = current_color

        self._generate_path_for_color(start, end, current_color, colors[1:])

    def _generate_path_for_color(
        self, 
        start: Tuple[int, int], 
        end: Tuple[int, int], 
        color_number: int,
        remaining_colors: List[int]
    ) -> None:
        """Generate and visualize path between endpoints for a specific color."""
        self.current_path = [start]

        def step_visualization():
            if self.current_path[-1] == end:
                self._mark_path_complete(self.current_path, color_number)
                QTimer.singleShot(500, lambda: self._visualize_color_paths(remaining_colors))
                return

            current = self.current_path[-1]
            next_point = self._calculate_next_move(current, end)

            if next_point and self._is_valid_move(next_point, color_number):
                self.grid_data.update_path(next_point[0], next_point[1], color_number)
                self.current_path.append(next_point)
                self.renderer.update()
                QTimer.singleShot(200, step_visualization)
            elif remaining_colors:
                self._visualize_color_paths(remaining_colors)

        step_visualization()

    def _is_valid_move(self, point: Tuple[int, int], color_number: int) -> bool:
        """Check if a move to the given point is valid."""
        row, col = point
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return False
        
        point_color = self.grid_data.get_color_point(row, col)
        if point_color != 0 and point_color != color_number:
            return False
            
        if (row, col) in self.current_path:
            return False
            
        return True

    def _calculate_next_move(self, current: Tuple[int, int], end: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Calculate the next move based on current position and target."""
        row, col = current
        target_row, target_col = end

        possible_moves = []
        
        if row != target_row:
            new_row = row + (1 if target_row > row else -1)
            possible_moves.append((new_row, col))
            
        if col != target_col:
            new_col = col + (1 if target_col > col else -1)
            possible_moves.append((row, new_col))

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (row + dr, col + dc)
            if new_pos not in possible_moves:
                possible_moves.append(new_pos)

        for move in possible_moves:
            if self._is_valid_move(move, self.current_color_number):
                return move

        return None

    def _mark_path_complete(self, path: List[Tuple[int, int]], color_number: int) -> None:
        """Mark a path as completed."""
        for point in path:
            self.grid_data.update_path(point[0], point[1], color_number)

        self.completed_paths.append((path, color_number))
        self.current_path.clear()
        self.renderer.update()

    def solve_with_python(self) -> None:
        """Solve the current board using the enhanced Python solver."""
        self._reset_game_state()
        board = self._get_current_board()
        solution = self._solve_flow_puzzle(board)
        
        if solution is None:
            self._show_message("No Solution", "The board does not have a solution.")
            return
            
        self.solution_paths = self._extract_solution_paths(solution)
        self._visualize_solution()

    def _get_current_board(self) -> List[List[str]]:
        """Convert current grid to string-based board format."""
        return [[str(self.grid_data.get_color_point(r, c)) 
                for c in range(self.grid_size)]
                for r in range(self.grid_size)]

    def _solve_flow_puzzle(self, board: List[List[str]]) -> Optional[List[List[str]]]:
        """Enhanced solver implementation."""
        def get_endpoints() -> Dict[str, List[Tuple[int, int]]]:
            endpoints = {}
            for r in range(len(board)):
                for c in range(len(board[0])):
                    if board[r][c] != '0':
                        endpoints.setdefault(board[r][c], []).append((r, c))
            return endpoints
        
        def get_colors() -> Set[str]:
            return {cell for row in board for cell in row if cell != '0'}
        
        def is_valid_move(pos: Tuple[int, int], color: str, current_board: List[List[str]]) -> bool:
            r, c = pos
            if not (0 <= r < len(current_board) and 0 <= c < len(current_board[0])):
                return False
            return current_board[r][c] == '0' or current_board[r][c] == color
        
        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            r, c = pos
            return [(r+dr, c+dc) for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]]
        
        def find_path(start: Tuple[int, int], end: Tuple[int, int], color: str, 
                     current_board: List[List[str]], remaining_colors: Set[str]) -> Optional[List[List[str]]]:
            queue = deque([(start, [start], set([start]), current_board)])
            
            while queue:
                current, path, visited, board_state = queue.popleft()
                
                if current == end:
                    new_board = copy.deepcopy(board_state)
                    for r, c in path:
                        new_board[r][c] = color
                    
                    if not remaining_colors:
                        return new_board
                    
                    next_solution = solve_with_remaining_colors(new_board, remaining_colors)
                    if next_solution:
                        return next_solution
                    continue
                
                neighbors = get_neighbors(current)
                neighbors.sort(key=lambda n: abs(n[0]-end[0]) + abs(n[1]-end[1]))
                
                for neighbor in neighbors:
                    if (neighbor not in visited and 
                        is_valid_move(neighbor, color, board_state)):
                        new_visited = visited | {neighbor}
                        new_path = path + [neighbor]
                        queue.append((neighbor, new_path, new_visited, board_state))
            
            return None
        
        def solve_with_remaining_colors(current_board: List[List[str]], 
                                      remaining_colors: Set[str]) -> Optional[List[List[str]]]:
            if not remaining_colors:
                return current_board
                
            color = remaining_colors.pop()
            endpoints = get_endpoints()
            start, end = endpoints[color]
            
            solution = find_path(start, end, color, current_board, remaining_colors)
            if solution:
                return solution
                
            remaining_colors.add(color)
            return None
        
        colors = get_colors()
        initial_board = copy.deepcopy(board)
        
        if not colors:
            return initial_board
            
        first_color = colors.pop()
        endpoints = get_endpoints()
        start, end = endpoints[first_color]
        
        return find_path(start, end, first_color, initial_board, colors)

    def _extract_solution_paths(self, solution: List[List[str]]) -> List[Tuple[List[Tuple[int, int]], int]]:
        """Extract paths for each color from the solution board."""
        paths = []
        colors = {int(cell) for row in solution for cell in row if cell != '0'}
        
        for color in colors:
            color_path = []
            start = None
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if str(color) == solution[r][c]:
                        if not start:
                            start = (r, c)
                        color_path.append((r, c))
            paths.append((color_path, color))
            
        return paths

    def _visualize_solution(self) -> None:
        """Visualize the solution paths sequentially."""
        if not self.solution_paths:
            return
            
        def visualize_next_path(path_index: int = 0) -> None:
            if path_index >= len(self.solution_paths):
                self._show_message("Solution Complete", "The puzzle has been solved!")
                return
                
            path, color = self.solution_paths[path_index]
            self._animate_path(path, color, lambda: visualize_next_path(path_index + 1))
            
        visualize_next_path()

    def _animate_path(self, path: List[Tuple[int, int]], color: int, callback: callable) -> None:
        """Animate a single path with color."""
        def animate_step(step: int = 0) -> None:
            if step >= len(path):
                callback()
                return
                
            r, c = path[step]
            self.grid_data.update_path(r, c, color)
            self.renderer.update()
            QTimer.singleShot(100, lambda: animate_step(step + 1))
            
        animate_step()

    def _show_message(self, title: str, message: str) -> None:
        """Display a message box with the given title and message."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.exec_()

    def _show_victory_message(self) -> None:
        """Display the victory message when all paths are complete."""
        self._show_message(
            "Path Generation Complete",
            "All paths have been successfully visualized!"
        )