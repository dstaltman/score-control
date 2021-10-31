# Main Layout for the Score Control.
#
# The purpose of this thing is to allow a place to control a lot of text files for OBS.
# Programmatic support of OBS to allow for text boxes and such to be updated from an
# external source rather than having to update each text box in OBS which is not
# super user friendly.

import sys

from PySide6.QtCore import Slot, SIGNAL, QTimer, QSettings, QSize, QPoint
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout

from fileManager import FileManager
from textToJsonWidget import TextToJsonWidget
from integerWidget import IntegerWidget
from loadFileWidget import LoadFileWidget


def create_json_widgets(layout, json_data: dict, data=None):
    for mainWidgetData in data:
        if mainWidgetData["type"] == "jsonWidget":
            jsonWidget = TextToJsonWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(jsonWidget)
        elif mainWidgetData["type"] == "integerWidget":
            intWidget = IntegerWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(intWidget)


class PlayerDetailsWidget(QWidget):
    def __init__(self, json_data: dict):
        QWidget.__init__(self)

        layoutData = {
            "mainLeftColumn": [
                {"type": "jsonWidget", "label": "Left Player", "jsonLocation": "left.playerName"},
                {"type": "jsonWidget", "label": "Left Army", "jsonLocation": "left.armyName"},
                {"type": "integerWidget", "label": "Left Command Points", "jsonLocation": "left.commandPoints"},
                {"type": "integerWidget", "label": "Left Total Points", "jsonLocation": "left.totalPoints"}
            ],
            "mainRightColumn": [
                {"type": "jsonWidget", "label": "Right Player", "jsonLocation": "right.playerName"},
                {"type": "jsonWidget", "label": "Right Army", "jsonLocation": "right.armyName"},
                {"type": "integerWidget", "label": "Right Command Points", "jsonLocation": "right.commandPoints"},
                {"type": "integerWidget", "label": "Right Total Points", "jsonLocation": "right.totalPoints"}
            ],
            "scoreWidgets": []
        }

        # Setup all the widgets in the layout
        layout = QHBoxLayout()

        # Left Player column
        leftColumn = QVBoxLayout()
        create_json_widgets(leftColumn, json_data, layoutData["mainLeftColumn"])
        layout.addLayout(leftColumn)

        # Right Player column
        rightColumn = QVBoxLayout()
        create_json_widgets(rightColumn, json_data, layoutData["mainRightColumn"])
        layout.addLayout(rightColumn)

        self.setLayout(layout)


# The guts of the score control. This class will deal with the main state of the
# system.
#
class ScoreControl(QMainWindow):
    # noinspection PyTypeChecker
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Score Control")
        self.fileManager = None
        self.json_data = None

        # Setup the window based on saved settings. Load any other
        # settings needed to start such as file locations
        self.read_settings()

        # Try to load a file now. Based on how it loads is what we'll do
        # with the widget later
        self.initialize_file_manager()

        # If we have a valid file, load default widget
        if self.fileManager.is_valid():
            playerWidget = PlayerDetailsWidget(self.json_data)
            self.setCentralWidget(playerWidget)
        else:
            loadWidget = LoadFileWidget("Load File", self.file_selected)
            self.setCentralWidget(loadWidget)

        # begin auto save
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.auto_save)
        self.timer.start(1000)

    # When the window is closed, save out its settings
    def closeEvent(self, event: QCloseEvent) -> None:
        self.write_settings()
        event.accept()

    def file_selected(self, filename: str):
        self.fileManager.set_file_path(filename)
        # If we have a valid file, load default widget
        if self.fileManager.is_valid():
            self.json_data = self.fileManager.get_json_data()
            playerWidget = PlayerDetailsWidget(self.json_data)
            self.setCentralWidget(playerWidget)

    @Slot()
    def auto_save(self):
        if isinstance(self.fileManager, FileManager):
            self.fileManager.write_file()

    def initialize_file_manager(self):
        # Load the file data and get it ready to send along
        self.fileManager = FileManager("")
        self.json_data = self.fileManager.get_json_data()

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
