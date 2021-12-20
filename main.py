# Main Layout for the Score Control.
#
# The purpose of this thing is to allow a place to control a lot of text files for OBS.
# Programmatic support of OBS to allow for text boxes and such to be updated from an
# external source rather than having to update each text box in OBS which is not
# super user friendly.

import sys

from PySide6.QtCore import Slot, SIGNAL, QTimer, QSettings, QSize, QPoint
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, \
    QPushButton, QGridLayout
import pydash
from pymitter import EventEmitter

import widgetHelpers
from fileManager import FileManager
from loadFileWidget import LoadFileWidget
from aosWidgets import setup_sigmar_windows
from widgets40k import setup_40k_windows


# Global emitter
ee = EventEmitter()


# The guts of the score control. This class will deal with the main state of the
# system.
#
class ScoreControl(QMainWindow):
    fileManager = None
    json_data = None
    score_details = None
    sigmar_battle_traits = None
    sigmar_grand_strategies = None

    # noinspection PyTypeChecker
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Score Control")

        # Setup the window based on saved settings. Load any other
        # settings needed to start such as file locations
        self.read_settings()

        # Try to load a file now. Based on how it loads is what we'll do
        # with the widget later
        self.initialize_file_manager()

        # Make the tabs Here
        self.tab_widget = QTabWidget()

        # Score Details Widget
        # If we have a valid file, load widget otherwise show file loader
        self.score_details = ScoreDetailsWidget(ee)
        if self.fileManager.is_valid():
            self.setup_windows()
        else:
            load_widget = LoadFileWidget("Load File", self.file_selected)
            self.score_details.set_body_widget(load_widget)
        self.tab_widget.addTab(self.score_details, "Score Control")

        # Put the tabs into the center widget
        self.setCentralWidget(self.tab_widget)

        # begin auto save
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.auto_save)
        self.timer.start(1000)

    # When the window is closed, save out its settings
    def closeEvent(self, event: QCloseEvent) -> None:
        self.write_settings()
        event.accept()

    # with a valid file manager figure out which screens to load
    def setup_windows(self):
        if self.json_data['dataType'] == 'sigmar':
            setup_sigmar_windows(self.json_data, self.tab_widget, self.score_details, ee)
        elif self.json_data['dataType'] == '40k':
            setup_40k_windows(self.json_data, self.tab_widget, self.score_details, ee)
        ee.emit("json_loaded", self.json_data)

    def file_selected(self, filename: str):
        self.fileManager.set_file_path(filename)
        # If we have a valid file, load default widget
        if self.fileManager.is_valid():
            self.json_data = self.fileManager.get_json_data()
            self.setup_windows()

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


class ScoreDetailsWidget(QWidget):
    body_widget = None
    body_layout = None

    def __init__(self, ee):
        super().__init__()

        self.body_layout = QVBoxLayout()
        self.setLayout(self.body_layout)

    def set_body_widget(self, w):
        if not isinstance(self.body_widget, type(None)):
            self.body_widget.hide()
            self.body_layout.removeWidget(self.body_widget)

        self.body_widget = w
        self.body_layout.addWidget(w)


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
