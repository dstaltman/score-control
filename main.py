# Main Layout for the Score Control.
#
# The purpose of this thing is to allow a place to control a lot of text files for OBS.
# Programmatic support of OBS to allow for text boxes and such to be updated from an
# external source rather than having to update each text box in OBS which is not
# super user friendly.

import sys

from PySide6.QtCore import Slot, SIGNAL, QTimer, QSettings, QSize, QPoint
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from fileManager import FileManager
from textToJsonWidget import TextToJsonWidget
from integerWidget import IntegerWidget


def create_json_widgets(layout, json_data: dict, data=None):
    for mainWidgetData in data["mainWidgets"]:
        if mainWidgetData["type"] == "jsonWidget":
            jsonWidget = TextToJsonWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(jsonWidget)
        elif mainWidgetData["type"] == "integerWidget":
            intWidget = IntegerWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(intWidget)


class PlayerDetailsWidget(QWidget):
    def __init__(self, json_data: dict):
        QWidget.__init__(self)

        data = {
            "mainWidgets": [
                {"type": "jsonWidget", "label": "Left Player", "jsonLocation": "left.playerName"},
                {"type": "jsonWidget", "label": "Left Army", "jsonLocation": "left.armyName"},
                {"type": "integerWidget", "label": "Left Player Command Points", "jsonLocation": "left.commandPoints"},
                {"type": "integerWidget", "label": "Left Player Total Points", "jsonLocation": "left.totalPoints"},

                {"type": "jsonWidget", "label": "Right Player", "jsonLocation": "right.playerName"},
                {"type": "jsonWidget", "label": "Right Army", "jsonLocation": "right.armyName"},
                {"type": "integerWidget", "label": "Right Player Command Points", "jsonLocation": "right.commandPoints"},
                {"type": "integerWidget", "label": "Right Player Total Points", "jsonLocation": "right.totalPoints"}
            ],
            "scoreWidgets": []
        }

        # Setup all the widgets in the layout
        layout = QVBoxLayout()
        create_json_widgets(layout, json_data, data)
        self.setLayout(layout)


# The guts of the score control. This class will deal with the main state of the
# system.
#
class ScoreControl(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Score Control")

        # Setup the window based on saved settings. Load any other
        # settings needed to start such as file locations
        self.read_settings()

        # Load the file data and get it ready to send along
        self.fileManager = FileManager("testdata.json")
        json_data = self.fileManager.get_json_data()

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit button
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)

        # Central widget
        widget = PlayerDetailsWidget(json_data)
        self.setCentralWidget(widget)

        # begin auto save
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.auto_save)
        self.timer.start(1000)

    # When the window is closed, saave out its settings
    def closeEvent(self, event: QCloseEvent) -> None:
        self.write_settings()
        event.accept()

    @Slot()
    def exit_app(self):
        QApplication.quit()

    @Slot()
    def auto_save(self):
        self.fileManager.write_file()

    def read_settings(self):
        settings = QSettings()
        settings.beginGroup("ScoreWindow")
        self.resize(settings.value("size", QSize(800, 600)))
        self.move(settings.value("position", QPoint(200, 200)))
        settings.endGroup()

    def write_settings(self):
        settings = QSettings()
        settings.beginGroup("ScoreWindow")
        settings.setValue("size", self.size())
        settings.setValue("position", self.pos())
        settings.endGroup()


if __name__ == '__main__':
    # QT Application
    app = QApplication(sys.argv)

    # Set QSettings global names
    app.setOrganizationName("Salmon Hammer")
    app.setOrganizationDomain("Score Control")

    # main window score control
    scoreControl = ScoreControl()
    scoreControl.show()

    sys.exit(app.exec())
