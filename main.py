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
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, \
    QPushButton, QGridLayout
from PySide6.QtCore import Qt
import pydash
from pymitter import EventEmitter

import widgetHelpers
from fileManager import FileManager
from loadFileWidget import LoadFileWidget
from listObjectEditorWidget import ListObjectEditorWidget
from integerWidget import IntegerWidget

# Global emitter
ee = EventEmitter()


# Has all the stuff for AoS player data
def build_field_test(item_json_location: str, json_blob: dict, dict_json_location: str):
    return lambda item: item_json_location not in item or item[item_json_location] \
                        in [None, "", "None", pydash.get(json_blob, dict_json_location)]


class PlayerDetailsWidget(QWidget):
    # Global Layout Data
    layout_data = {
        "mainLeftColumn": [
            {"type": "text", "label": "Left Player", "jsonLocation": "left.playerName"},
            {"type": "combo", "label": "Left Army", "jsonLocation": "left.armyName",
             "itemsLocation": "sigmarFactions"},
            {"type": "integer", "label": "Left Command Points", "jsonLocation": "left.commandPoints", "resetValue": 0},
            {"type": "combo", "label": "Left Grand Strategy", "jsonLocation": "left.grandStrategyName",
             "itemsLocation": "sigmarGrandStrategies", "filterFunc": lambda: True},
            {"type": "integer", "label": "Grand Strategy Score", "jsonLocation": "left.grandStrategyScore",
             "resetValue": 0},

        ],
        "mainRightColumn": [
            {"type": "text", "label": "Right Player", "jsonLocation": "right.playerName"},
            {"type": "combo", "label": "Right Army", "jsonLocation": "right.armyName",
             "itemsLocation": "sigmarFactions"},
            {"type": "integer", "label": "Right Command Points", "jsonLocation": "right.commandPoints",
             "resetValue": 0},
            {"type": "combo", "label": "Right Grand Strategy", "jsonLocation": "right.grandStrategyName",
             "itemsLocation": "sigmarGrandStrategies", "filterFunc": lambda: True},
            {"type": "integer", "label": "Grand Strategy Score", "jsonLocation": "right.grandStrategyScore",
             "resetValue": 0},
        ]
    }

    # Round data
    left_round_data = [
        {"type": "integer", "label": "Round {roundNum} Primary",
         "jsonLocation": "left.aosRoundScores[{roundIndex}].primaryScore", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary",
         "jsonLocation": "left.aosRoundScores[{roundIndex}].secondaryScore", "resetValue": 0},
        {"type": "combo", "label": "Round {roundNum} Secondary",
         "jsonLocation": "left.aosRoundScores[{roundIndex}].secondaryName", "itemsLocation": "sigmarBattleTraits",
         "resetValue": "------", "filterFunc": lambda: True},
        {"type": "integer", "label": "Round {roundNum} Bonus",
         "jsonLocation": "left.aosRoundScores[{roundIndex}].bonusScore", "resetValue": 0},
    ]
    right_round_data = [
        {"type": "integer", "label": "Round {roundNum} Primary",
         "jsonLocation": "right.aosRoundScores[{roundIndex}].primaryScore", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary",
         "jsonLocation": "right.aosRoundScores[{roundIndex}].secondaryScore", "resetValue": 0},
        {"type": "combo", "label": "Round {roundNum} Secondary",
         "jsonLocation": "right.aosRoundScores[{roundIndex}].secondaryName", "itemsLocation": "sigmarBattleTraits",
         "resetValue": "------", "filterFunc": lambda: True},
        {"type": "integer", "label": "Round {roundNum} Bonus",
         "jsonLocation": "right.aosRoundScores[{roundIndex}].bonusScore", "resetValue": 0},
    ]

    def __init__(self, json_data: dict):
        QWidget.__init__(self)

        self.widget_list = []
        self.json_data = json_data

        # Update Widgets lists - replace parts of the lists as needed to be more programmatic (seems shitty)
        left_edit_lists = [
            self.layout_data["mainLeftColumn"],
            self.left_round_data
        ]
        for widgetList in left_edit_lists:
            for widgetData in widgetList:
                if "filterFunc" not in widgetData:
                    continue
                if callable(widgetData["filterFunc"]):
                    widgetData["filterFunc"] = build_field_test("armyType", json_data, "left.armyName")
        right_edit_lists = [
            self.layout_data["mainRightColumn"],
            self.right_round_data
        ]
        for widgetList in right_edit_lists:
            for widgetData in widgetList:
                if "filterFunc" not in widgetData:
                    continue
                if callable(widgetData["filterFunc"]):
                    widgetData["filterFunc"] = build_field_test("armyType", json_data, "right.armyName")

        # Setup all the widgets in the layout
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)

        # Reset button
        reset_button = QPushButton("Reset Scoreboard")
        reset_button.clicked.connect(self.reset_scores)
        layout.addWidget(reset_button, 0, 0, 1, 2)

        # Turn Number Widget
        round_widget = IntegerWidget("Round Number", json_data, "roundNum",
                                     reset_value="1")
        layout.addWidget(round_widget, 1, 0, 1, 2)

        # No Active Player button
        no_active_player = QPushButton("No active player")
        no_active_player.clicked.connect(self.no_player_active)
        layout.addWidget(no_active_player, 2, 0, 1, 2)

        # Top / Bottom Buttons
        turn_top_button = QPushButton("Set Round to TOP")
        turn_top_button.clicked.connect(self.set_top_round)
        layout.addWidget(turn_top_button, 3, 0, 1, 1)

        turn_bot_button = QPushButton("Set Round to BOT")
        turn_bot_button.clicked.connect(self.set_bot_round)
        layout.addWidget(turn_bot_button, 3, 1, 1, 1)

        # Left Player column
        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignTop)

        # Left Player active button at the top
        left_active_button = QPushButton("Set Left Player Active")
        left_active_button.clicked.connect(self.left_player_active)
        left_column.addWidget(left_active_button)

        # Main Left Widgets
        widgetHelpers.create_json_widgets(left_column, json_data, self.layout_data["mainLeftColumn"], self.widget_list)

        # Round widgets
        left_tabs = QTabWidget()
        # Round data
        for i in range(5):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            cur_round_data = copy.deepcopy(self.left_round_data)
            for wData in cur_round_data:
                for key in wData.keys():
                    if type(wData[key]) is str:
                        wData[key] = wData[key].format(roundNum=i + 1, roundIndex=i)
            widgetHelpers.create_json_widgets(tab_layout, json_data, cur_round_data, self.widget_list)
            tab.setLayout(tab_layout)
            left_tabs.addTab(tab, "Round " + str(i + 1) + " Scoring")
        left_column.addWidget(left_tabs)

        layout.addLayout(left_column, 4, 0)

        # Right Player column
        right_column = QVBoxLayout()
        right_column.setAlignment(Qt.AlignTop)

        # Right Player active button at the top
        right_active_button = QPushButton("Set Right Player Active")
        right_active_button.clicked.connect(self.right_player_active)
        right_column.addWidget(right_active_button)

        widgetHelpers.create_json_widgets(right_column, json_data, self.layout_data["mainRightColumn"],
                                          self.widget_list)

        # Round widgets
        right_tabs = QTabWidget()
        for i in range(5):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            cur_round_data = copy.deepcopy(self.right_round_data)
            for wData in cur_round_data:
                for key in wData.keys():
                    if type(wData[key]) is str:
                        wData[key] = wData[key].format(roundNum=i + 1, roundIndex=i)
            widgetHelpers.create_json_widgets(tab_layout, json_data, cur_round_data, self.widget_list)
            tab.setLayout(tab_layout)
            right_tabs.addTab(tab, "Round " + str(i + 1) + " Scoring")
        right_column.addWidget(right_tabs)

        layout.addLayout(right_column, 4, 1)

        self.setLayout(layout)

    @Slot()
    def reset_scores(self):
        for widget in self.widget_list:
            widget.reset_data()

    @Slot()
    def set_top_round(self):
        pydash.set_(self.json_data, "roundOrder", "TOP")

    @Slot()
    def set_bot_round(self):
        pydash.set_(self.json_data, "roundOrder", "BOT")

    @Slot()
    def left_player_active(self):
        pydash.set_(self.json_data, "left.playerStatus", "ACTIVE")
        pydash.set_(self.json_data, "right.playerStatus", "")

    @Slot()
    def right_player_active(self):
        pydash.set_(self.json_data, "left.playerStatus", "")
        pydash.set_(self.json_data, "right.playerStatus", "ACTIVE")

    @Slot()
    def no_player_active(self):
        pydash.set_(self.json_data, "left.playerStatus", "")
        pydash.set_(self.json_data, "right.playerStatus", "")


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
    sigmar_fac_layout = []

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
                                              self.sigmar_fac_layout)
        self.body_widget = sig_obj_list
        self.body_layout.addWidget(sig_obj_list)

    def setup_missing_widget(self):
        if not isinstance(self.body_widget, type(None)):
            self.body_layout.removeWidget(self.body_widget)

        w = QLabel("File not loaded. Please load file in first tab to start editing!")
        self.body_widget = w
        self.body_layout.addWidget(w)


class SigmarGrandStrategyEditor(QWidget):
    body_widget = None
    body_layout = None
    json_data = None
    json_location = None
    sigmar_obj_layout = [
        {"type": "text", "label": "Description", "jsonLocation": "description"},
        {"type": "integer", "label": "Point Value", "jsonLocation": "pointValue"},
        {"type": "combo", "label": "Army Type", "jsonLocation": "armyType",
         "itemsLocation": "sigmarFactions"},
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

        sig_obj_list = ListObjectEditorWidget("Grand Strategies", self.json_data, self.json_location,
                                              self.sigmar_obj_layout)
        self.body_widget = sig_obj_list
        self.body_layout.addWidget(sig_obj_list)

    def setup_missing_widget(self):
        if not isinstance(self.body_widget, type(None)):
            self.body_layout.removeWidget(self.body_widget)

        w = QLabel("File not loaded. Please load file in first tab to start editing!")
        self.body_widget = w
        self.body_layout.addWidget(w)


class SigmarBattleTraitEditor(QWidget):
    body_widget = None
    body_layout = None
    json_data = None
    json_location = None
    sigmar_obj_layout = [
        {"type": "text", "label": "Battle Trait Description", "jsonLocation": "description"},
        {"type": "integer", "label": "Point Value", "jsonLocation": "pointValue"},
        {"type": "combo", "label": "Army Type", "jsonLocation": "armyType",
         "itemsLocation": "sigmarFactions"},
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

        sig_obj_list = ListObjectEditorWidget("Battle Traits", self.json_data, self.json_location,
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
        self.score_details = ScoreDetailsWidget()
        if self.fileManager.is_valid():
            player_widget = PlayerDetailsWidget(self.json_data)
            self.score_details.set_body_widget(player_widget)
        else:
            load_widget = LoadFileWidget("Load File", self.file_selected)
            self.score_details.set_body_widget(load_widget)
        self.tab_widget.addTab(self.score_details, "Score Control")

        # AoS Grand Strategy Editor
        self.sigmar_grand_strategies = SigmarGrandStrategyEditor(self.json_data, "sigmarGrandStrategies")
        self.tab_widget.addTab(self.sigmar_grand_strategies, "Sigmar Grand Strategies")

        # AoS Battle Traits Editor
        self.sigmar_battle_traits = SigmarBattleTraitEditor(self.json_data, "sigmarBattleTraits")
        self.tab_widget.addTab(self.sigmar_battle_traits, "Sigmar Battle Traits")

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
            player_widget = PlayerDetailsWidget(self.json_data)
            self.score_details.set_body_widget(player_widget)
            self.sigmar_battle_traits.set_json_data(self.json_data)
            self.sigmar_grand_strategies.set_json_data(self.json_data)
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
