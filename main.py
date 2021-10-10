# Main Layout for the Score Control.
#
# The purpose of this thing is to allow a place to control a lot of text files for OBS.
# Programmatic support of OBS to allow for text boxes and such to be updated from an
# external source rather than having to update each text box in OBS which is not
# super user friendly.

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from textToFileWidget import TextToFileWidget


class PlayerDetailsWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # Hard coded file names
        self._data = {
            "Left Player": "C:\\StreamTextFiles\\LeftPlayerName.txt",
            "Left Army": "C:\\StreamTextFiles\\LeftArmyName.txt",
            "Right Player": "C:\\StreamTextFiles\\RightPlayerName.txt",
            "Right Army": "C:\\StreamTextFiles\\RightArmyName.txt"
        }

        layout = QVBoxLayout()
        self.create_text_widgets(layout)
        self.setLayout(layout)

    def create_text_widgets(self, layout, data=None):
        data = self._data if not data else data
        for label, file in data.items():
            text_widget = TextToFileWidget(file, label)
            layout.addWidget(text_widget)


class ScoreControl(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Score Control")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit button
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)

        # Central widget
        widget = PlayerDetailsWidget()
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self):
        QApplication.quit()


if __name__ == '__main__':
    # QT Application
    app = QApplication(sys.argv)

    # main window score control
    scoreControl = ScoreControl()
    scoreControl.resize(800, 600)
    scoreControl.show()

    sys.exit(app.exec())

