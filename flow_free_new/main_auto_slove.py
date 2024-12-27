import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from GameAutoSlove import GameController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flow Free Path Visualization")
        self.setGeometry(100, 100, 800, 800)

        # Tạo GameController
        self.game_controller = GameController(grid_size=10, window_size=800)

        # Cài đặt giao diện
        self.init_ui()

    def init_ui(self):
        # Widget trung tâm chứa renderer và các nút điều khiển
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Thêm renderer (giao diện chính của game)
        layout.addWidget(self.game_controller.renderer)

        # Thêm nút "Visualize Paths"
        visualize_button = QPushButton("Visualize Paths")
        visualize_button.clicked.connect(self.game_controller.visualize_paths)
        layout.addWidget(visualize_button)

        # Cài đặt layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
