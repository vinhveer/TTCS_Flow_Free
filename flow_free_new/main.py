import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

from GameController import GameController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flow Free Game")
        self.setGeometry(100, 100, 800, 800)  # Kích thước cửa sổ

        # Tạo một đối tượng GameController
        self.game_controller = GameController()

        # Thêm widget renderer của GameController vào MainWindow
        self.setCentralWidget(self.game_controller.renderer)

    def mousePressEvent(self, event: QMouseEvent):
        """Xử lý sự kiện nhấn chuột"""
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            self.game_controller.handle_mouse_press(x, y)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Xử lý sự kiện di chuyển chuột"""
        x, y = event.x(), event.y()
        self.game_controller.handle_mouse_move(x, y)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Xử lý sự kiện nhả chuột"""
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            self.game_controller.handle_mouse_release(x, y)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
