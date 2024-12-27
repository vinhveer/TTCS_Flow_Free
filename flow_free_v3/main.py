import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import Qt
from GameController import GameController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flow Free Game")
        self.setGeometry(100, 100, 1000, 800)
        
        # Tạo layout chính
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Widget game
        self.game_widget = QWidget()
        self.game_layout = QVBoxLayout(self.game_widget)
        self.game_layout.setContentsMargins(0, 0, 0, 0)
        
        # Khởi tạo biến game_controller
        self.game_controller = None
        self._initialize_game("hard", 2)

        # Control panel
        control_panel = self._create_control_panel()

        # Thêm vào layout chính
        main_layout.addWidget(self.game_widget, stretch=4)
        main_layout.addWidget(control_panel, stretch=1)

    def _cleanup_game(self):
        """Dọn dẹp game controller và renderer cũ"""
        if self.game_controller is not None:
            # Xóa renderer khỏi layout
            if self.game_layout.count() > 0:
                old_renderer = self.game_layout.takeAt(0).widget()
                if old_renderer:
                    old_renderer.setParent(None)  # Ngắt kết nối với parent
                    old_renderer.deleteLater()    # Xóa renderer
            
            # Cleanup game controller
            self.game_controller.setParent(None)  # Ngắt kết nối với parent
            self.game_controller.deleteLater()    # Xóa game controller
            self.game_controller = None

    def _initialize_game(self, difficulty, level):
        """Khởi tạo hoặc cập nhật trò chơi."""
        # Dọn dẹp game cũ
        # self._cleanup_game()

        # Tạo GameController mới
        self.game_controller = GameController.setup(self, difficulty, level)
        self.game_layout.addWidget(self.game_controller.renderer)

    def _create_control_panel(self):
        """Tạo bảng điều khiển."""
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        control_layout.addWidget(QLabel("Độ khó:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        control_layout.addWidget(self.difficulty_combo)

        control_layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems([str(i) for i in range(1, 6)])
        control_layout.addWidget(self.level_combo)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.start_new_game)
        control_layout.addWidget(self.play_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_game)
        control_layout.addWidget(self.reset_button)

        control_layout.addStretch()
        return control_panel

    def start_new_game(self):
        """Bắt đầu trò chơi mới với thông tin từ bảng điều khiển."""
        difficulty = self.difficulty_combo.currentText().lower()
        level = int(self.level_combo.currentText())
        self._initialize_game(difficulty, level)

    def reset_game(self):
        """Đặt lại trò chơi hiện tại."""
        if self.game_controller:
            self.game_controller.reset_game()

    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        self._cleanup_game()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()