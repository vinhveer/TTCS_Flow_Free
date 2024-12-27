from PyQt5.QtWidgets import QMessageBox

from GridData import GridData
from GameRender import GameRenderer

# Các hằng số
WINDOW_SIZE = 800
GRID_SIZE = GridData().getSize()
CELL_SIZE = (WINDOW_SIZE - 100) // GRID_SIZE
WINDOW_PADDING = (WINDOW_SIZE - (CELL_SIZE * GRID_SIZE)) // 2
CIRCLE_SIZE = CELL_SIZE * 0.6
PATH_WIDTH = min(30, CELL_SIZE // 5)

class GameController:
    def __init__(self):
        self.grid_data = GridData()
        
        self.endpoints = []
        self.completed_paths = []
        self.current_path = []
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.is_drawing = False
        self.path_connections = set()

        self.renderer = GameRenderer(self)
        
        self.setup()

    def setup(self):
        """Khởi tạo trò chơi"""
        self.endpoints = []
        self.completed_paths = []
        self.current_path = []
        self.path_connections = set()
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.is_drawing = False

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color_number = self.grid_data.get_color_point(row, col)
                if color_number > 0:
                    self.endpoints.append((row, col, color_number))

        self.renderer.update()

    def handle_mouse_press(self, x, y):
        """Xử lý sự kiện nhấn chuột"""
        col = (x - WINDOW_PADDING) // CELL_SIZE
        row = (y - WINDOW_PADDING) // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            # Kiểm tra nếu nhấn vào một đường đã vẽ
            path, color = self._get_path_at_point(row, col)
            if path:
                self._remove_path(path, color)
                return

            # Nếu nhấn vào một điểm bắt đầu, bắt đầu vẽ đường mới
            color_number = self.grid_data.get_color_point(row, col)
            if color_number > 0:
                self.grid_data.clear_path_for_color(color_number)

                self.is_drawing = True
                self.current_path = [(row, col)]
                self.current_color = self.grid_data.get_color(color_number)
                self.current_color_number = color_number

                self.grid_data.update_path(row, col, color_number)
                self.renderer.update()

    def handle_mouse_move(self, x, y):
        """Xử lý sự kiện di chuyển chuột"""
        if not self.is_drawing or not self.current_path:
            return

        col = (x - WINDOW_PADDING) // CELL_SIZE
        row = (y - WINDOW_PADDING) // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            # Nếu điểm hiện tại đã có trong đường đi thì bỏ qua
            if (row, col) in self.current_path:
                return

            # Kiểm tra nước đi có hợp lệ không
            if self._is_valid_move(row, col):
                # Kiểm tra nếu gặp điểm đích cùng màu
                if self.grid_data.is_endpoint(row, col, self.current_color_number):
                    self.current_path.append((row, col))
                    self.grid_data.update_path(row, col, self.current_color_number)
                    
                    # Tự động kết thúc đường
                    self._complete_current_path()
                    return

                # Thêm điểm vào đường đi
                self.current_path.append((row, col))
                self.grid_data.update_path(row, col, self.current_color_number)
                self.renderer.update()

    def handle_mouse_release(self, x, y):
        """Xử lý sự kiện nhả chuột"""
        if not self.is_drawing:
            return

        col = (x - WINDOW_PADDING) // CELL_SIZE
        row = (y - WINDOW_PADDING) // CELL_SIZE

        # Kiểm tra xem có nối được đến điểm đích không
        if (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and 
            self.grid_data.is_endpoint(row, col, self.current_color_number) and
            len(self.current_path) > 1):
            # Nếu đúng điểm đích thì kết thúc
            self.current_path.append((row, col))
            self.grid_data.update_path(row, col, self.current_color_number)
            self._complete_current_path()
        else:
            # Không nối được -> Xóa đường
            self._clear_current_path()

    def _is_valid_move(self, row, col):
        """Kiểm tra nước đi có hợp lệ không"""
        if not self.current_path:
            return (
                self.grid_data.get_color_point(row, col) == self.current_color_number and
                self.grid_data.path_grid[row][col] == 0
            )

        last_row, last_col = self.current_path[-1]
        
        move_valid = (
            ((abs(row - last_row) == 1 and col == last_col) or 
             (abs(col - last_col) == 1 and row == last_row)) or
            
            (self.grid_data.is_endpoint(row, col, self.current_color_number) and 
             len(self.current_path) > 1)
        )

        point_not_in_path = (row, col) not in self.current_path

        color_check = (
            self.grid_data.get_color_point(row, col) == 0 or
            self.grid_data.get_color_point(row, col) == self.current_color_number
        )

        return move_valid and point_not_in_path and color_check

    def _complete_current_path(self):
        """Hoàn thiện đường đi"""
        if (len(self.current_path) > 1 and 
            self.grid_data.get_color_point(*self.current_path[0]) == self.current_color_number and
            self.grid_data.get_color_point(*self.current_path[-1]) == self.current_color_number):

            self.completed_paths.append((self.current_path, self.current_color))
            
            if len(self.completed_paths) == len(set(endpoint[2] for endpoint in self.endpoints)):
                self._show_victory_message()

        # Reset trạng thái
        self._reset_drawing_state()

    def _clear_current_path(self):
        """Xóa đường đi hiện tại"""
        if self.current_color_number:
            self.grid_data.clear_path_for_color(self.current_color_number)
        
        self._reset_drawing_state()

    def _reset_drawing_state(self):
        """Đặt lại trạng thái vẽ"""
        self.current_path = []
        self.is_drawing = False
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.renderer.update()

    def _remove_path(self, path, color):
        """Xóa một đường đã hoàn thành"""
        self.completed_paths.remove((path, color))
        
        for r, c in path:
            self.grid_data.path_grid[r][c] = 0
        
        self.renderer.update()

    def _get_path_at_point(self, row, col):
        """Kiểm tra xem điểm (row, col) thuộc đường nào."""
        for path, color in self.completed_paths:
            if (row, col) in path:
                return path, color
        return None, None

    def _show_victory_message(self):
        """Hiển thị thông báo chiến thắng"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Congratulations!")
        msg_box.setInformativeText("You've completed the Flow Free game!")
        msg_box.setWindowTitle("Victory")
        msg_box.exec_()
