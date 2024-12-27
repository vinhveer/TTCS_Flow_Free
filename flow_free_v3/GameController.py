from PyQt5.QtWidgets import QMessageBox, QWidget, QPushButton

from GridData import GridData
from GameRender import GameRenderer
from Slove import Slove

# Các hằng số
WINDOW_SIZE = 800

class GameController:
    def __init__(self, mode, level):
        self.grid_data = GridData()
        self.grid_data_original = GridData()

        self.grid_data.set_mode(mode)
        self.grid_data.set_level(level)

        self.grid_data_original.set_mode(mode)
        self.grid_data_original.set_level(level)
        
        self.endpoints = []
        self.completed_paths = []
        self.current_path = []
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.is_drawing = False
        self.path_connections = set()

        self.renderer = GameRenderer(self)
        self._update_grid_parameters()

        # Thêm nút Auto Solve
        self.auto_solve_button = QPushButton('Auto Solve', self.renderer)
        self.auto_solve_button.clicked.connect(self.handle_auto_solve)
        self.auto_solve_button.setGeometry(WINDOW_SIZE - 120, 10, 110, 30)
        
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

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color_number = self.grid_data.get_color_point(row, col)
                if color_number > 0:
                    self.endpoints.append((row, col, color_number))

        self._update_grid_parameters()
        
        self.renderer.update()
    
    def _update_grid_parameters(self):
        self.grid_size = self.grid_data.getSize()
        self.cell_size = (WINDOW_SIZE - 100) // self.grid_size
        self.window_padding = (WINDOW_SIZE - (self.cell_size * self.grid_size)) // 2
        self.circle_size = self.cell_size * 0.6
        self.path_width = min(30, self.cell_size // 5)

    def handle_mouse_press(self, x, y):
        """Xử lý sự kiện nhấn chuột"""
        col = (x - self.window_padding) // self.cell_size
        row = (y - self.window_padding) // self.cell_size

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
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

        col = (x - self.window_padding) // self.cell_size
        row = (y - self.window_padding) // self.cell_size

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            # Nếu điểm hiện tại đã có trong đường đi thì bỏ qua
            if (row, col) in self.current_path:
                # Nếu quay lại điểm trước đó, xóa điểm cuối cùng
                if len(self.current_path) > 1 and (row, col) == self.current_path[-2]:
                    last_row, last_col = self.current_path[-1]
                    self.grid_data.path_grid[last_row][last_col] = 0
                    self.current_path.pop()
                    self.renderer.update()
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

        col = (x - self.window_padding) // self.cell_size
        row = (y - self.window_padding) // self.cell_size

        # Kiểm tra xem có nối được đến điểm đích không
        if (0 <= row < self.grid_size and 0 <= col < self.grid_size and 
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
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return False

        if not self.current_path:
            return (
                self.grid_data.get_color_point(row, col) == self.current_color_number and
                self.grid_data.path_grid[row][col] == 0
            )

        last_row, last_col = self.current_path[-1]
        
        # Chỉ cho phép di chuyển theo chiều ngang hoặc dọc
        is_horizontal = row == last_row and abs(col - last_col) == 1
        is_vertical = col == last_col and abs(row - last_row) == 1
        
        # Kiểm tra điểm đích 
        is_endpoint = (
            self.grid_data.is_endpoint(row, col, self.current_color_number) and 
            len(self.current_path) > 1 and
            (is_horizontal or is_vertical)  # Điểm đích cũng phải theo chiều dọc hoặc ngang
        )
        
        # Kiểm tra không đi qua ô đã có đường khác
        path_is_clear = True
        if is_horizontal or is_vertical:
            if self.grid_data.path_grid[row][col] != 0:
                if not self.grid_data.is_endpoint(row, col, self.current_color_number):
                    path_is_clear = False

        # Điều kiện hợp lệ
        move_valid = (is_horizontal or is_vertical)  
        point_not_in_path = (row, col) not in self.current_path
        color_check = (
            self.grid_data.get_color_point(row, col) == 0 or
            self.grid_data.get_color_point(row, col) == self.current_color_number
        )

        return (move_valid or is_endpoint) and point_not_in_path and color_check and path_is_clear

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
    
    def reset_game(self):
        """Reset game hiện tại"""
        self.setup()

    def _show_victory_message(self):
        """Hiển thị thông báo chiến thắng"""
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Congratulations!")
        msg_box.setInformativeText("You've completed the Flow Free game!")
        msg_box.setWindowTitle("Victory")
        msg_box.exec_()

    def show_answer(self, answer_grid):
        """Hiển thị đáp án"""
        # Xóa hết đường đi hiện tại
        self.completed_paths.clear()
        self.grid_data.path_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Dictionary lưu điểm đầu-cuối của mỗi màu
        endpoints = {}  # {color: (start_point, end_point)}
        # Dictionary lưu đường đi của mỗi màu theo thứ tự
        paths = {}      # {color: [list of ordered points]}

        # Tìm điểm đầu và cuối từ grid ban đầu
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color = self.grid_data.get_color_point(row, col)
                if color > 0:
                    if color not in endpoints:
                        endpoints[color] = (row, col)  # điểm đầu
                    else:
                        endpoints[color] = (endpoints[color], (row, col))  # cập nhật điểm cuối

        # Tìm đường đi từ điểm đầu đến điểm cuối cho mỗi màu
        for color, (start, end) in endpoints.items():
            current = start
            path = [start]
            paths[color] = path
            
            # Tìm đường đi theo answer_grid
            while current != end:
                # Kiểm tra 4 hướng: phải, xuống, trái, lên
                for next_row, next_col in [(current[0], current[1]+1), 
                                         (current[0]+1, current[1]),
                                         (current[0], current[1]-1),
                                         (current[0]-1, current[1])]:
                    if (0 <= next_row < self.grid_size and 
                        0 <= next_col < self.grid_size and
                        answer_grid[next_row][next_col] == color and
                        (next_row, next_col) not in path):
                        path.append((next_row, next_col))
                        current = (next_row, next_col)
                        break

        # Vẽ đường đi theo thứ tự đã tìm được
        for color, path in paths.items():
            # Cập nhật path_grid
            for row, col in path:
                self.grid_data.path_grid[row][col] = color
            # Thêm vào completed_paths
            self.completed_paths.append((path, self.grid_data.get_color(color)))

        self.renderer.update()

    def handle_auto_solve(self):
        """Xử lý khi nhấn nút Auto Solve"""        
        # Lấy đáp án tương ứng với mode và level
        print("Solving...")

        answer_grid = Slove(self.grid_data_original.get_original_grid(), self.grid_size, self.grid_size)
        print("Answer found!")
        print(answer_grid)
        if answer_grid:
            self.show_answer(answer_grid)

    def show_answer(self, answer_grid):
        """Hiển thị đáp án theo hướng từ điểm đầu đến điểm cuối"""
        # Reset trạng thái
        self.completed_paths.clear()
        self.grid_data.path_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Tìm điểm đầu và điểm cuối cho mỗi màu
        endpoints = {}  # {color: (start_point, end_point)}
        
        # Quét để tìm các điểm đầu-cuối
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color = self.grid_data.get_color_point(row, col)
                if color > 0:
                    if color not in endpoints:
                        endpoints[color] = [(row, col)]  # điểm đầu
                    else:
                        endpoints[color].append((row, col))  # điểm cuối

        # Tìm đường đi cho từng màu
        for color, points in endpoints.items():
            if len(points) == 2:
                start, end = points
                path = self._find_path(answer_grid, start, end, color)
                if path:
                    # Cập nhật path_grid
                    for r, c in path:
                        self.grid_data.path_grid[r][c] = color
                    # Thêm vào completed_paths
                    self.completed_paths.append((path, self.grid_data.get_color(color)))

        self.renderer.update()

    def _find_path(self, answer_grid, start, end, color):
        """Tìm đường đi từ điểm start đến end theo màu color"""
        path = [start]
        current = start
        
        # Tiếp tục tìm cho đến khi đến điểm cuối
        while current != end:
            next_point = None
            # Kiểm tra 4 hướng: phải, xuống, trái, lên
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_row = current[0] + dr
                next_col = current[1] + dc
                
                # Kiểm tra điểm tiếp theo có hợp lệ không
                if (0 <= next_row < self.grid_size and 
                    0 <= next_col < self.grid_size and
                    answer_grid[next_row][next_col] == color and
                    (next_row, next_col) not in path):
                    next_point = (next_row, next_col)
                    break
            
            if next_point:
                path.append(next_point)
                current = next_point
            else:
                # Không tìm thấy đường đi
                return None
                
        return path