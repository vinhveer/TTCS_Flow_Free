from PyQt5.QtWidgets import QApplication
from FlowFreeGame import FlowFreeGame

if __name__ == "__main__":
    app = QApplication([])
    window = FlowFreeGame()
    window.show()
    app.exec_()