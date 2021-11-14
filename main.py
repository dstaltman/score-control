# Main Layout for the Score Control.
#
# The purpose of this thing is to allow a place to control a lot of text files for OBS.
# Programmatic support of OBS to allow for text boxes and such to be updated from an
# external source rather than having to update each text box in OBS which is not
# super user friendly.

import sys
import copy

from PySide6.QtCore import Slot, SIGNAL, QTimer, QSettings, QSize, QPoint
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel
from PySide6.QtCore import Qt
from pymitter import EventEmitter

import widgetHelpers
from fileManager import FileManager
from loadFileWidget import LoadFileWidget
from listObjectEditorWidget import ListObjectEditorWidget


# Global emitter
ee = EventEmitter()


# Has all the stuff for AoS player data
class PlayerDetailsWidget(QWidget):
    def __init__(self, json_data: dict):
        QWidget.__init__(self)

        layoutData = {
            "mainLeftColumn": [
                {"type": "text", "label": "Left Player", "jsonLocation": "left.playerName"},
                {'type': 'combo', 'label': 'Left Army', 'jsonLocation': 'left.armyName',
                 'itemsLocation': 'sigmarFactions'},
                {"type": "integer", "label": "Left Command Points", "jsonLocation": "left.commandPoints"},
                {"type": "integer", "label": "Left Total Points", "jsonLocation": "left.totalPoints"},
                {"type": "combo", "label": "Left Grand Strategy", "jsonLocation": "left.grandStrategy",
                 "itemsLocation": "sigmarObjectives", "itemFilterType": "grand strategy"},
                {"type": "integer", "label": "Left Grand Strategy", "jsonLocation": "left.grandStrategyScore"},

            ],
            "mainRightColumn": [
                {"type": "text", "label": "Right Player", "jsonLocation": "right.playerName"},
                {'type': 'combo', 'label': 'Right Army', 'jsonLocation': 'right.armyName',
                 'itemsLocation': 'sigmarFactions'},
                {"type": "integer", "label": "Right Command Points", "jsonLocation": "right.commandPoints"},
                {"type": "integer", "label": "Right Total Points", "jsonLocation": "right.totalPoints"},
                {"type": "combo", "label": "Right Grand Strategy", "jsonLocation": "right.grandStrategy",
                 "itemsLocation": "sigmarObjectives", "itemFilterType": "grand strategy"},
                {"type": "integer", "label": "Right Grand Strategy", "jsonLocation": "right.grandStrategyScore"},
            ],
            "scoreWidgets": []
        }

        # Setup all the widgets in the layout
        layout = QHBoxLayout()

        # Left Player column
        leftColumn = QVBoxLayout()
        leftColumn.setAlignment(Qt.AlignTop)
        # Main Left Widgets
        widgetHelpers.create_json_widgets(leftColumn, json_data, layoutData["mainLeftColumn"])

        # Round widgets
        leftTabs = QTabWidget()
        # Round data
        roundData = [
            {"type": "integer", "label": "Round {roundNum} Primary",
             "jsonLocation": "left.aosRoundScores[{roundIndex}].primaryScore"},
            {"type": "integer", "label": "Round {roundNum} Secondary",
             "jsonLocation": "left.aosRoundScores[{roundIndex}].secondaryScore"},
            {"type": "combo", "label": "Round {roundNum} Secondary",
             "jsonLocation": "left.aosRoundScores[{roundIndex}].secondaryName", "itemsLocation": "sigmarObjectives",
             "itemFilterType": "battle tactic"},
            {"type": "integer", "label": "Round {roundNum} Bonus",
             "jsonLocation": "left.aosRoundScores[{roundIndex}].bonusScore"},
        ]
        for i in range(5):
            tab = QWidget()
            tabLayout = QVBoxLayout()
            curRoundData = copy.deepcopy(roundData)
            for wData in curRoundData:
                for key in wData.keys():
                    wData[key] = wData[key].format(roundNum=i+1, roundIndex=i)
            widgetHelpers.create_json_widgets(tabLayout, json_data, curRoundData)
            tab.setLayout(tabLayout)
            leftTabs.addTab(tab, "Round " + str(i+1) + " Scoring")
        leftColumn.addWidget(leftTabs)

        layout.addLayout(leftColumn)

        # Right Player column
        rightColumn = QVBoxLayout()
        rightColumn.setAlignment(Qt.AlignTop)
        widgetHelpers.create_json_widgets(rightColumn, json_data, layoutData["mainRightColumn"])

        # Round widgets
        rightTabs = QTabWidget()
        # Round data
        roundData = [
            {"type": "integer", "label": "Round {roundNum} Primary",
             "jsonLocation": "right.aosRoundScores[{roundIndex}].primaryScore"},
            {"type": "integer", "label": "Round {roundNum} Secondary",
             "jsonLocation": "right.aosRoundScores[{roundIndex}].secondaryScore"},
            {"type": "combo", "label": "Round {roundNum} Secondary",
             "jsonLocation": "right.aosRoundScores[{roundIndex}].secondaryName", "itemsLocation": "sigmarObjectives",
             "itemFilterType": "battle tactic"},
            {"type": "integer", "label": "Round {roundNum} Bonus",
             "jsonLocation": "right.aosRoundScores[{roundIndex}].bonusScore"},
        ]
        for i in range(5):
            tab = QWidget()
            tabLayout = QVBoxLayout()
            curRoundData = copy.deepcopy(roundData)
            for wData in curRoundData:
                for key in wData.keys():
                    wData[key] = wData[key].format(roundNum=i + 1, roundIndex=i)
            widgetHelpers.create_json_widgets(tabLayout, json_data, curRoundData)
            tab.setLayout(tabLayout)
            rightTabs.addTab(tab, "Round " + str(i + 1) + " Scoring")
        rightColumn.addWidget(rightTabs)

        layout.addLayout(rightColumn)

        self.setLayout(layout)


class ScoreDetailsWidget(QWidget):
    body_widget = None
    body_layout = None

    def __init__(self):
        super().__init__()

        self.body_layout = QVBoxLayout()
        self.setLayout(self.body_layout)

    def set_body_widget(self, w):
        if not isinstance(self.body_widget, type(None)):
            self.body_widget.hide()
            self.body_layout.removeWidget(self.body_widget)

        self.body_widget = w
        self.body_layout.addWidget(w)


class SigmarFactionsEditor(QWidget):
    body_widget = None
    body_layout = None
    json_data = None
    json_location = None
    sigmar_obj_layout = []

    def __init__(self, json_data, json_location):
        super().__init__()
        self.body_layout = QVBoxLayout()
        self.setLayout(self.body_layout)

        self.json_data = json_data
        self.json_location = json_location

        def json_data_handler(in_data):
            print("Json Data Handler Called")
            self.set_json_data(in_data)
        ee.on("json_loaded", json_data_handler)

        if isinstance(json_data, type(None)):
            self.setup_missing_widget()
        else:
            self.setup_editor_widget()

    def set_json_data(self, json_data):
        self.json_data = json_data
        self.setup_editor_widget()

    def setup_editor_widget(self):
        if not isinstance(self.body_widget, type(None)):
            self.body_widget.hide()
            self.body_layout.removeWidget(self.body_widget)

        sig_obj_list = ListObjectEditorWidget("AoS Factions", self.json_data, self.json_location,
                                              self.sigmar_obj_layout)
        self.body_widget = sig_obj_list
        self.body_layout.addWidget(sig_obj_list)

    def setup_missing_widget(self):
        if not isinstance(self.body_widget, type(None)):
            self.body_layout.removeWidget(self.body_widget)

        w = QLabel("File not loaded. Please load file in first tab to start editing!")
        self.body_widget = w
        self.body_layout.addWidget(w)


class SigmarObjectivesEditor(QWidget):
    body_widget = None
    body_layout = None
    json_data = None
    json_location = None
    sigmar_obj_layout = [
        {'type': 'text', 'label': 'Objective Description', 'jsonLocation': 'description'},
        {'type': 'integer', 'label': 'Point Value', 'jsonLocation': 'pointValue'},
        {'type': 'combo', 'label': 'Objective Type', 'jsonLocation': 'type',
            'itemsLocation': 'sigmarObjectiveTypes'},
    ]

    def __init__(self, json_data, json_location):
        super().__init__()
        self.body_layout = QVBoxLayout()
        self.setLayout(self.body_layout)

        self.json_data = json_data
        self.json_location = json_location
        if isinstance(json_data, type(None)):
            self.setup_missing_widget()
        else:
            self.setup_editor_widget()

    def set_json_data(self, json_data):
        self.json_data = json_data
        self.setup_editor_widget()

    def setup_editor_widget(self):
        if not isinstance(self.body_widget, type(None)):
            self.body_widget.hide()
            self.body_layout.removeWidget(self.body_widget)

        sig_obj_list = ListObjectEditorWidget("AoS Objectives", self.json_data, self.json_location,
                                              self.sigmar_obj_layout)
        self.body_widget = sig_obj_list
        self.body_layout.addWidget(sig_obj_list)

    def setup_missing_widget(self):
        if not isinstance(self.body_widget, type(None)):
            self.body_layout.removeWidget(self.body_widget)

        w = QLabel("File not loaded. Please load file in first tab to start editing!")
        self.body_widget = w
        self.body_layout.addWidget(w)


# The guts of the score control. This class will deal with the main state of the
# system.
#
class ScoreControl(QMainWindow):
    fileManager = None
    json_data = None
    score_details = None
    sigmar_objectives = None

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
        self.score_details = ScoreDetailsWidget()
        if self.fileManager.is_valid():
            playerWidget = PlayerDetailsWidget(self.json_data)
            self.score_details.set_body_widget(playerWidget)
        else:
            loadWidget = LoadFileWidget("Load File", self.file_selected)
            self.score_details.set_body_widget(loadWidget)
        self.tab_widget.addTab(self.score_details, "Score Control")

        # AoS Objective Editor
        self.sigmar_objectives = SigmarObjectivesEditor(self.json_data, "sigmarObjectives")
        self.tab_widget.addTab(self.sigmar_objectives, "Sigmar Objective Editor")

        # AoS Faction Editor
        self.sigmar_factions = SigmarFactionsEditor(self.json_data, "sigmarFactions")
        self.tab_widget.addTab(self.sigmar_factions, "Sigmar Factions Editor")

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

    def file_selected(self, filename: str):
        self.fileManager.set_file_path(filename)
        # If we have a valid file, load default widget
        if self.fileManager.is_valid():
            self.json_data = self.fileManager.get_json_data()
            playerWidget = PlayerDetailsWidget(self.json_data)
            self.score_details.set_body_widget(playerWidget)
            self.sigmar_objectives.set_json_data(self.json_data)
            ee.emit("json_loaded", self.json_data)

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
