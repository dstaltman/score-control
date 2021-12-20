# Widget layout for 40K
#
# This file will create all the widgets and tabs and such to make an 40k editor

import copy

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, \
    QPushButton, QGridLayout

import widgetHelpers

from PySide6.QtCore import Qt
from listObjectEditorWidget import ListObjectEditorWidget


# Layouts for various WidgetDataLoaders
primary_objectives_layout = [
    {"type": "text", "label": "Description", "jsonLocation": "description"},
]
secondary_objectives_layout = [
    {"type": "text", "label": "Description", "jsonLocation": "description"},
    {"type": "combo", "label": "Army Type", "jsonLocation": "armyType",
     "itemsLocation": "40kFactions"},
]
faction_layout = [
    {"type": "text", "label": "Description", "jsonLocation": "description"},
]


# Static function to setup all the widgets used in editing 40k
def setup_40k_windows(json_data, tab_widget, score_details, ee):
    player_widget = PlayerDetailsWidget(json_data, ee)
    score_details.set_body_widget(player_widget)

    # 40k Primary Missions
    primary_objectives = ListObjectEditorWidget("40K Primary Objectives Editor", json_data,
                                                "40kPrimaryObjectives",
                                                primary_objectives_layout)
    tab_widget.addTab(primary_objectives, "40K Primary Objectives")

    # 40k Secondary Objectives
    secondary_objectives = ListObjectEditorWidget("40K Secondary Objectives Editor", json_data,
                                                  "40kSecondaryObjectives",
                                                  secondary_objectives_layout)
    tab_widget.addTab(secondary_objectives, "40K Secondary Objectives")

    # 40k Faction Editor
    factions = ListObjectEditorWidget("40K Factions Editor", json_data, "40kFactions", faction_layout)
    tab_widget.addTab(factions, "40K Factions Editor")


# Class to handle scoring for 40k
class PlayerDetailsWidget(QWidget):
    # Global Layout Data
    layout_data = {
        "mainLeftColumn": [
            {"type": "text", "label": "Left Player", "jsonLocation": "left.playerName"},
            {"type": "combo", "label": "Left Army", "jsonLocation": "left.armyName",
             "itemsLocation": "40kFactions"},
            {"type": "integer", "label": "Left Command Points", "jsonLocation": "left.commandPoints", "resetValue": 0},
            {"type": "combo", "label": "Secondary 1",
             "jsonLocation": "left.40kRoundScores[{roundIndex}].secondaryName0",
             "itemsLocation": "40kSecondaryObjectives", "resetValue": "------", "filterFunc": lambda: True},
            {"type": "combo", "label": "Secondary 2",
             "jsonLocation": "left.40kRoundScores[{roundIndex}].secondaryName1",
             "itemsLocation": "40kSecondaryObjectives", "resetValue": "------", "filterFunc": lambda: True},
            {"type": "combo", "label": "Secondary 3",
             "jsonLocation": "left.40kRoundScores[{roundIndex}].secondaryName2",
             "itemsLocation": "40kSecondaryObjectives", "resetValue": "------", "filterFunc": lambda: True},
        ],
        "mainRightColumn": [
            {"type": "text", "label": "Right Player", "jsonLocation": "right.playerName"},
            {"type": "combo", "label": "Right Army", "jsonLocation": "right.armyName",
             "itemsLocation": "40kFactions"},
            {"type": "integer", "label": "Right Command Points", "jsonLocation": "right.commandPoints",
             "resetValue": 0},
            {"type": "combo", "label": "Secondary 1",
             "jsonLocation": "right.40kRoundScores[{roundIndex}].secondaryName0",
             "itemsLocation": "40kSecondaryObjectives", "resetValue": "------", "filterFunc": lambda: True},
            {"type": "combo", "label": "Secondary 2",
             "jsonLocation": "right.40kRoundScores[{roundIndex}].secondaryName1",
             "itemsLocation": "40kSecondaryObjectives", "resetValue": "------", "filterFunc": lambda: True},
            {"type": "combo", "label": "Secondary 3",
             "jsonLocation": "right.40kRoundScores[{roundIndex}].secondaryName2",
             "itemsLocation": "40kSecondaryObjectives", "resetValue": "------", "filterFunc": lambda: True},
        ]
    }

    # Round data
    left_round_data = [
        {"type": "integer", "label": "Round {roundNum} Primary",
         "jsonLocation": "left.40kRoundScores[{roundIndex}].primaryScore", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary 1",
         "jsonLocation": "left.40kRoundScores[{roundIndex}].secondaryScore0", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary 2",
         "jsonLocation": "left.40kRoundScores[{roundIndex}].secondaryScore1", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary 3",
         "jsonLocation": "left.40kRoundScores[{roundIndex}].secondaryScore2", "resetValue": 0},
    ]
    right_round_data = [
        {"type": "integer", "label": "Round {roundNum} Primary",
         "jsonLocation": "right.40kRoundScores[{roundIndex}].primaryScore", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary 1",
         "jsonLocation": "right.40kRoundScores[{roundIndex}].secondaryScore0", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary 2",
         "jsonLocation": "right.40kRoundScores[{roundIndex}].secondaryScore1", "resetValue": 0},
        {"type": "integer", "label": "Round {roundNum} Secondary 3",
         "jsonLocation": "right.40kRoundScores[{roundIndex}].secondaryScore2", "resetValue": 0},
    ]

    def __init__(self, json_data: dict, ee):
        QWidget.__init__(self)

        self.widget_list = []

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
                    widgetData["filterFunc"] = widgetHelpers.build_field_test("armyType", json_data, "left.armyName")
        right_edit_lists = [
            self.layout_data["mainRightColumn"],
            self.right_round_data
        ]
        for widgetList in right_edit_lists:
            for widgetData in widgetList:
                if "filterFunc" not in widgetData:
                    continue
                if callable(widgetData["filterFunc"]):
                    widgetData["filterFunc"] = widgetHelpers.build_field_test("armyType", json_data, "right.armyName")

        # Setup all the widgets in the layout
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)

        # Reset button
        reset_button = QPushButton("Reset Scoreboard")
        reset_button.clicked.connect(self.reset_scores)
        layout.addWidget(reset_button, 0, 0, 1, 2)

        # Left Player column
        left_column = QVBoxLayout()
        left_column.setAlignment(Qt.AlignTop)

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

        layout.addLayout(left_column, 1, 0)

        # Right Player column
        right_column = QVBoxLayout()
        right_column.setAlignment(Qt.AlignTop)
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

        layout.addLayout(right_column, 1, 1)

        self.setLayout(layout)

    @Slot()
    def reset_scores(self):
        for widget in self.widget_list:
            widget.reset_data()
