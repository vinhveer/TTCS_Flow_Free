from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath, QLinearGradient
from PyQt5.QtCore import Qt, QRectF

from GridData import GridData

# Các hằng số
WINDOW_SIZE = 800
GRID_SIZE = GridData().getSize()
CELL_SIZE = (WINDOW_SIZE - 100) // GRID_SIZE
WINDOW_PADDING = (WINDOW_SIZE - (CELL_SIZE * GRID_SIZE)) // 2
CIRCLE_SIZE = CELL_SIZE * 0.6
PATH_WIDTH = min(30, CELL_SIZE // 5)

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath, QLinearGradient
from PyQt5.QtCore import Qt, QRectF

# Các hằng số giữ nguyên

class GameRenderer(QWidget):
    def __init__(self, game_controller):
        super().__init__()
        self.game_controller = game_controller
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)

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
        for row in range(GRID_SIZE + 1):
            y = row * CELL_SIZE + WINDOW_PADDING
            painter.drawLine(WINDOW_PADDING, y, WINDOW_PADDING + GRID_SIZE * CELL_SIZE, y)

        for col in range(GRID_SIZE + 1):
            x = col * CELL_SIZE + WINDOW_PADDING
            painter.drawLine(x, WINDOW_PADDING, x, WINDOW_PADDING + GRID_SIZE * CELL_SIZE)

    def _draw_endpoints(self, painter):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color_number = self.game_controller.grid_data.get_color_point(row, col)
                if color_number > 0:
                    color = self.game_controller.grid_data.get_color(color_number)
                    self._draw_single_endpoint(painter, row, col, color)

    def _draw_single_endpoint(self, painter, row, col, color):
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

    def _draw_path_with_shadow(self, painter, path, color: QColor):
        if len(path) > 1:
            # Tạo đường với shadow
            shadow_color = QColor(0, 0, 0, 50)
            shadow_path = self._create_rounded_path(path, offset=3)
            painter.setPen(QPen(shadow_color, PATH_WIDTH, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(shadow_path)

            # Vẽ đường chính
            main_path = self._create_rounded_path(path)
            painter.setPen(QPen(color, PATH_WIDTH, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(main_path)

    def _create_rounded_path(self, path, offset=0):
        path_obj = QPainterPath()
        if len(path) < 2:
            return path_obj

        def get_coords(point):
            return (
                point[1] * CELL_SIZE + CELL_SIZE // 2 + WINDOW_PADDING + offset, 
                point[0] * CELL_SIZE + CELL_SIZE // 2 + WINDOW_PADDING + offset
            )

        start_x, start_y = get_coords(path[0])
        path_obj.moveTo(start_x, start_y)

        for i in range(1, len(path)):
            prev_point = get_coords(path[i-1])
            curr_point = get_coords(path[i])
            path_obj.lineTo(curr_point[0], curr_point[1])

        return path_obj