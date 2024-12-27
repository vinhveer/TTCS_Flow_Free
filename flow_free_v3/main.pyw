import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QComboBox, QLabel)
from PyQt5.QtCore import Qt
from GameController import GameController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flow Free Game")
        self.setGeometry(100, 100, 1000, 800)

        # Định nghĩa difficulty_levels là thuộc tính của class
        self.difficulty_levels = {
            "Easy": ["1", "2", "3", "4"],
            "Medium": ["1", "2", "3", "4", "5"],
            "Hard": ["1", "2", "3", "4", "5"],
            "Expert": ["1", "2", "3"]
        }

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        
        # Create main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)

        # Control panel on left
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)

        # Game widget
        self.game_widget = QWidget()
        self.game_layout = QVBoxLayout(self.game_widget)
        self.game_layout.setContentsMargins(0, 0, 0, 0)
        self.game_layout.setSpacing(0)
        
        # Initialize game
        self._initialize_game("easy", 1)
        main_layout.addWidget(self.game_widget)

    def _initialize_game(self, difficulty, level):
        if self.game_layout.count() > 0:
            old_renderer = self.game_layout.takeAt(0).widget()
            if old_renderer:
                old_renderer.deleteLater()
                
        self.game_controller = GameController(difficulty, level)
        self.game_layout.addWidget(self.game_controller.renderer)

    def update_levels(self, difficulty):
        self.level_combo.clear()
        self.level_combo.addItems(self.difficulty_levels[difficulty])

    def _create_control_panel(self):
        control_panel = QWidget()
        control_panel.setFixedWidth(300)
        control_panel.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                background-color: #f5f6fa;
            }
            
            QLabel {
                font-size: 25px;
                color: #2c3e50;
                padding: 5px 0;
            }
            
            QLabel#title {
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                margin-bottom: 20px;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 25px;
                font-weight: bold;
                border-radius: 8px;
                margin: 10px 0;
                min-height: 50px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton#resetButton {
                background-color: #e74c3c;
            }
            
            QPushButton#resetButton:hover {
                background-color: #c0392b;
            }
            
            QComboBox {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 12px 20px;
                min-height: 45px;
                font-size: 18px;
                margin: 5px 0;
            }
            
            QComboBox:hover {
                border-color: #3498db;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 40px;
                font-size: 30px;    
            }
            
            QComboBox:on {
                border-color: #3498db;
            }
        """)
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 30, 20, 30)
        control_layout.setSpacing(15)

        # Title
        title_label = QLabel("Flow Free Game")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(title_label)
        
        # Difficulty section
        difficulty_label = QLabel("Difficulty:")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(list(self.difficulty_levels.keys()))
        
        control_layout.addWidget(difficulty_label)
        control_layout.addWidget(self.difficulty_combo)
        
        # Level section
        level_label = QLabel("Level:")
        self.level_combo = QComboBox()
        # Khởi tạo với levels của difficulty đầu tiên
        self.level_combo.addItems(self.difficulty_levels["Easy"])
        
        control_layout.addWidget(level_label)
        control_layout.addWidget(self.level_combo)
        
        # Kết nối signal để cập nhật levels khi difficulty thay đổi
        self.difficulty_combo.currentTextChanged.connect(self.update_levels)
        
        # Add some space before buttons
        control_layout.addSpacing(20)
        
        # Buttons
        self.play_button = QPushButton("Play")
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("resetButton")
        
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.reset_button)
        
        self.play_button.clicked.connect(self.start_new_game)
        self.reset_button.clicked.connect(self.reset_game)
        
        control_layout.addStretch()
        
        return control_panel

    def start_new_game(self):
        difficulty = self.difficulty_combo.currentText().lower()
        level = int(self.level_combo.currentText())
        self._initialize_game(difficulty, level)

    def reset_game(self):
        self.game_controller.reset_game()

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()