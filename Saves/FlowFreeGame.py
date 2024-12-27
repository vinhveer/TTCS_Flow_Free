from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath, QLinearGradient
from PyQt5.QtCore import Qt, QRectF

from GridData import GridData

# Fixed window size
WINDOW_SIZE = 800

# Dynamic cell and grid calculations
GRID_SIZE = GridData().getSize()
CELL_SIZE = (WINDOW_SIZE - 100) // GRID_SIZE  # Adjust cell size to fit window
WINDOW_PADDING = (WINDOW_SIZE - (CELL_SIZE * GRID_SIZE)) // 2
CIRCLE_SIZE = CELL_SIZE * 0.6
PATH_WIDTH = min(30, CELL_SIZE // 5)  # Scale path width proportionally

class FlowFreeGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)

        self.grid_data = GridData()

        self.endpoints = []
        self.completed_paths = []
        self.current_path = []
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.is_drawing = False
        self.path_connections = set()

        self.setup()

    def setup(self):
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

        self.update()

    def clear_current_path(self):
        """Xóa đường đi hiện tại và reset trạng thái"""
        if self.current_color_number:
            self.grid_data.clear_path_for_color(self.current_color_number)
        
        self.current_path = []
        self.is_drawing = False
        self.current_color = None
        self.current_color_number = None
        self.start_point = None
        self.update()

    def is_valid_move(self, row, col):
        """Kiểm tra nước đi có hợp lệ không"""
        # Nếu đường đi đang rỗng, kiểm tra xem có phải điểm đầu của màu không
        if not self.current_path:
            return (
                self.grid_data.get_color_point(row, col) == self.current_color_number and
                self.grid_data.path_grid[row][col] == 0
            )

        last_row, last_col = self.current_path[-1]
        
        # Mở rộng điều kiện di chuyển
        move_valid = (
            # Di chuyển 1 ô theo hàng hoặc cột
            ((abs(row - last_row) == 1 and col == last_col) or 
             (abs(col - last_col) == 1 and row == last_row)) or
            
            # Cho phép nhảy đến điểm đích cùng màu nếu chưa có đường
            (self.grid_data.is_endpoint(row, col, self.current_color_number) and 
             len(self.current_path) > 1)
        )

        # Không được đi vào điểm đã có trong đường đi
        point_not_in_path = (row, col) not in self.current_path

        # Kiểm tra màu điểm
        color_check = (
            self.grid_data.get_color_point(row, col) == 0 or  # Ô trống
            self.grid_data.get_color_point(row, col) == self.current_color_number  # Điểm đích cùng màu
        )

        return move_valid and point_not_in_path and color_check

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        col = (x - WINDOW_PADDING) // CELL_SIZE
        row = (y - WINDOW_PADDING) // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            # Kiểm tra nếu nhấn vào một đường đã vẽ
            path, color = self.get_path_at_point(row, col)
            if path:
                # Xóa đường khỏi danh sách completed_paths
                self.completed_paths.remove((path, color))
                
                # Xóa dấu vết trên path_grid
                for r, c in path:
                    self.grid_data.path_grid[r][c] = 0
                
                self.update()
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
                self.update()


    def mouseMoveEvent(self, event):
        if not self.is_drawing or not self.current_path:
            return

        col = (event.x() - WINDOW_PADDING) // CELL_SIZE
        row = (event.y() - WINDOW_PADDING) // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            # Nếu điểm hiện tại đã có trong đường đi thì bỏ qua
            if (row, col) in self.current_path:
                return

            # Kiểm tra nước đi có hợp lệ không
            if self.is_valid_move(row, col):
                # Kiểm tra nếu gặp điểm đích cùng màu
                if self.grid_data.is_endpoint(row, col, self.current_color_number):
                    self.current_path.append((row, col))
                    self.grid_data.update_path(row, col, self.current_color_number)
                    
                    # Tự động kết thúc đường
                    self.complete_current_path()
                    return

                # Thêm điểm vào đường đi
                self.current_path.append((row, col))
                self.grid_data.update_path(row, col, self.current_color_number)
                self.update()

    def mouseReleaseEvent(self, event):
        if not self.is_drawing:
            return

        col = (event.x() - WINDOW_PADDING) // CELL_SIZE
        row = (event.y() - WINDOW_PADDING) // CELL_SIZE

        # Kiểm tra xem có nối được đến điểm đích không
        if (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and 
            self.grid_data.is_endpoint(row, col, self.current_color_number) and
            len(self.current_path) > 1):
            # Nếu đúng điểm đích thì kết thúc
            self.current_path.append((row, col))
            self.grid_data.update_path(row, col, self.current_color_number)
            self.complete_current_path()
        else:
            # Không nối được -> Xóa đường
            self.clear_current_path()

    def complete_current_path(self):
        """Hoàn thiện đường đi"""
        if (len(self.current_path) > 1 and 
            self.grid_data.get_color_point(*self.current_path[0]) == self.current_color_number and
            self.grid_data.get_color_point(*self.current_path[-1]) == self.current_color_number):

            # Thêm đường đi hoàn chỉnh
            self.completed_paths.append((self.current_path, self.current_color))
            
            # Kiểm tra chiến thắng
            if len(self.completed_paths) == len(set(endpoint[2] for endpoint in self.endpoints)):
                self.show_victory_message()

        # Reset trạng thái
        self.current_path = []
        self.current_color = None
        self.current_color_number = None
        self.is_drawing = False
        self.start_point = None
        self.update()

    def show_victory_message(self):
        QMessageBox.information(self, "Congratulations!", "You've completed the Flow Free game!")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Vẽ nền lưới
        gradient = QLinearGradient(0, 0, WINDOW_SIZE, WINDOW_SIZE)
        gradient.setColorAt(0, QColor(240, 240, 240))
        gradient.setColorAt(1, QColor(220, 220, 220))
        painter.fillRect(self.rect(), gradient)

        # Vẽ đường lưới
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.SolidLine))
        for row in range(GRID_SIZE + 1):
            y = row * CELL_SIZE + WINDOW_PADDING
            painter.drawLine(WINDOW_PADDING, y, WINDOW_PADDING + GRID_SIZE * CELL_SIZE, y)

        for col in range(GRID_SIZE + 1):
            x = col * CELL_SIZE + WINDOW_PADDING
            painter.drawLine(x, WINDOW_PADDING, x, WINDOW_PADDING + GRID_SIZE * CELL_SIZE)

        # Vẽ đường đã hoàn thành
        for path, color in self.completed_paths:
            self.draw_path_with_shadow(painter, path, color)

        # Vẽ đường đang vẽ
        if len(self.current_path) > 1:
            self.draw_path_with_shadow(painter, self.current_path, self.current_color)

        # Vẽ các điểm đầu
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color_number = self.grid_data.get_color_point(row, col)
                if color_number > 0:
                    color = self.grid_data.get_color(color_number)
                    self.draw_endpoint(painter, row, col, color)

    def draw_endpoint(self, painter, row, col, color):
        x = col * CELL_SIZE + WINDOW_PADDING
        y = row * CELL_SIZE + WINDOW_PADDING

        # Soft shadow
        shadow_offset = 3
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(100, 100, 100, 50))
        painter.drawEllipse(QRectF(
            x + (CELL_SIZE - CIRCLE_SIZE) / 2 + shadow_offset, 
            y + (CELL_SIZE - CIRCLE_SIZE) / 2 + shadow_offset, 
            CIRCLE_SIZE, CIRCLE_SIZE
        ))

        # Radial gradient for endpoint
        gradient = QRadialGradient(
            x + CELL_SIZE // 2, 
            y + CELL_SIZE // 2, 
            CIRCLE_SIZE // 2
        )
        gradient.setColorAt(0, color.lighter(130))
        gradient.setColorAt(1, color.darker(110))

        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QRectF(
            x + (CELL_SIZE - CIRCLE_SIZE) / 2, 
            y + (CELL_SIZE - CIRCLE_SIZE) / 2, 
            CIRCLE_SIZE, CIRCLE_SIZE
        ))

    def create_rounded_path(self, path, offset=0):
        path_obj = QPainterPath()
        if len(path) < 2:
            return path_obj

        # Calculate path coordinates with offset
        def get_coords(point):
            return (
                point[1] * CELL_SIZE + CELL_SIZE // 2 + WINDOW_PADDING + offset, 
                point[0] * CELL_SIZE + CELL_SIZE // 2 + WINDOW_PADDING + offset
            )

        # Move to start point
        start_x, start_y = get_coords(path[0])
        path_obj.moveTo(start_x, start_y)

        # Create path with sharp, rounded corners
        for i in range(1, len(path)):
            prev_point = get_coords(path[i-1])
            curr_point = get_coords(path[i])

            path_obj.lineTo(curr_point[0], curr_point[1])

        return path_obj

    def draw_path_with_shadow(self, painter, path, color):
        if len(path) > 1:
            # Shadow effect
            shadow_color = QColor(0, 0, 0, 50)
            shadow_path = self.create_rounded_path(path, offset=3)
            painter.setPen(QPen(shadow_color, PATH_WIDTH, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(shadow_path)

            # Main Path with smooth gradient
            main_path = self.create_rounded_path(path)
            painter.setPen(QPen(color, PATH_WIDTH, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(main_path)

    def get_path_at_point(self, row, col):
        """Kiểm tra xem điểm (row, col) thuộc đường nào."""
        for path, color in self.completed_paths:
            if (row, col) in path:
                return path, color
        return None, None
