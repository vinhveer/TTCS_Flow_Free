from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath, QLinearGradient
from PyQt5.QtCore import Qt, QRectF

WINDOW_SIZE = 800  # Keep this as global constant

class GameRenderer(QWidget):
    def __init__(self, game_controller):
        super().__init__()
        self.game_controller = game_controller
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
        self.setMouseTracking(True)
        self._update_grid_parameters()

    def _update_grid_parameters(self):
        self.grid_size = self.game_controller.grid_data.getSize()
        self.cell_size = (WINDOW_SIZE - 100) // self.grid_size
        self.window_padding = (WINDOW_SIZE - (self.cell_size * self.grid_size)) // 2
        self.circle_size = self.cell_size * 0.6
        self.path_width = min(30, self.cell_size // 5)
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Vẽ nền lưới
        self._draw_background(painter)
        
        # Vẽ lưới
        self._draw_grid(painter)
        
        # Vẽ các đường đã hoàn thành
        for path, color_number in self.game_controller.completed_paths:
            color = self.game_controller.grid_data.get_color(color_number)
            self._draw_path_with_shadow(painter, path, color)

        # Vẽ đường đang vẽ
        if len(self.game_controller.current_path) > 1 and self.game_controller.current_color_number:
            color = self.game_controller.grid_data.get_color(self.game_controller.current_color_number)
            self._draw_path_with_shadow(painter, 
                                      self.game_controller.current_path, 
                                      color)

        # Vẽ các điểm đầu
        self._draw_endpoints(painter)

    def _draw_background(self, painter):
        gradient = QLinearGradient(0, 0, WINDOW_SIZE, WINDOW_SIZE)
        gradient.setColorAt(0, QColor(240, 240, 240))
        gradient.setColorAt(1, QColor(220, 220, 220))
        painter.fillRect(self.rect(), gradient)

    def _draw_grid(self, painter):
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.SolidLine))
        for row in range(self.grid_size + 1):
            y = row * self.cell_size + self.window_padding
            painter.drawLine(self.window_padding, y, 
                           self.window_padding + self.grid_size * self.cell_size, y)

        for col in range(self.grid_size + 1):
            x = col * self.cell_size + self.window_padding
            painter.drawLine(x, self.window_padding, 
                           x, self.window_padding + self.grid_size * self.cell_size)

    def _draw_endpoints(self, painter):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color_number = self.game_controller.grid_data.get_color_point(row, col)
                if color_number > 0:
                    color = self.game_controller.grid_data.get_color(color_number)
                    self._draw_single_endpoint(painter, row, col, color)

    def _draw_single_endpoint(self, painter, row, col, color):
        x = col * self.cell_size + self.window_padding
        y = row * self.cell_size + self.window_padding

        # Soft shadow
        shadow_offset = 3
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(100, 100, 100, 50))
        painter.drawEllipse(QRectF(
            x + (self.cell_size - self.circle_size) / 2 + shadow_offset, 
            y + (self.cell_size - self.circle_size) / 2 + shadow_offset, 
            self.circle_size, self.circle_size
        ))

        # Radial gradient for endpoint
        gradient = QRadialGradient(
            x + self.cell_size // 2, 
            y + self.cell_size // 2, 
            self.circle_size // 2
        )
        gradient.setColorAt(0, color.lighter(130))
        gradient.setColorAt(1, color.darker(110))

        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QRectF(
            x + (self.cell_size - self.circle_size) / 2, 
            y + (self.cell_size - self.circle_size) / 2, 
            self.circle_size, self.circle_size
        ))

    def _draw_path_with_shadow(self, painter, path, color: QColor):
        if len(path) > 1:
            # Tạo đường với shadow
            shadow_color = QColor(0, 0, 0, 50)
            shadow_path = self._create_rounded_path(path, offset=3)
            painter.setPen(QPen(shadow_color, self.path_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(shadow_path)

            # Vẽ đường chính
            main_path = self._create_rounded_path(path)
            painter.setPen(QPen(color, self.path_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(main_path)

    def _create_rounded_path(self, path, offset=0):
        path_obj = QPainterPath()
        if len(path) < 2:
            return path_obj

        def get_coords(point):
            return (
                point[1] * self.cell_size + self.cell_size // 2 + self.window_padding + offset, 
                point[0] * self.cell_size + self.cell_size // 2 + self.window_padding + offset
            )

        start_x, start_y = get_coords(path[0])
        path_obj.moveTo(start_x, start_y)

        for i in range(1, len(path)):
            prev_point = get_coords(path[i-1])
            curr_point = get_coords(path[i])
            path_obj.lineTo(curr_point[0], curr_point[1])

        return path_obj

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        self.game_controller.handle_mouse_press(x, y)

    def mouseMoveEvent(self, event):
        x, y = event.x(), event.y()
        self.game_controller.handle_mouse_move(x, y)

    def mouseReleaseEvent(self, event):
        x, y = event.x(), event.y()
        self.game_controller.handle_mouse_release(x, y)