# Layout for AoS
#
# This file will create all the widgets and tabs and such to make an AoS editor

import copy

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QGridLayout

import widgetHelpers
import pydash

from PySide6.QtCore import Qt

from integerWidget import IntegerWidget
from listObjectEditorWidget import ListObjectEditorWidget


# Layouts for various WidgetDataLoaders
faction_layout = []
grand_strategy_layout = [
    {"type": "text", "label": "Description", "jsonLocation": "description"},
    {"type": "integer", "label": "Point Value", "jsonLocation": "pointValue"},
    {"type": "combo", "label": "Army Type", "jsonLocation": "armyType",
     "itemsLocation": "sigmarFactions"},
]
battle_trait_layout = [
    {"type": "text", "label": "Battle Trait Description", "jsonLocation": "description"},
    {"type": "integer", "label": "Point Value", "jsonLocation": "pointValue"},
    {"type": "combo", "label": "Army Type", "jsonLocation": "armyType",
     "itemsLocation": "sigmarFactions"},
]


def setup_sigmar_windows(json_data, tab_widget, score_details, ee):
    player_widget = SigmarPlayerDetailsWidget(json_data, ee)
    score_details.set_body_widget(player_widget)

    # AoS Grand Strategy Editor
    sigmar_grand_strategies = ListObjectEditorWidget("Grand Strategies", json_data, "sigmarGrandStrategies",
                                                     grand_strategy_layout)
    tab_widget.addTab(sigmar_grand_strategies, "Sigmar Grand Strategies")

    # AoS Battle Traits Editor
    sigmar_battle_traits = ListObjectEditorWidget("Battle Traits", json_data, "sigmarBattleTraits", battle_trait_layout)
    tab_widget.addTab(sigmar_battle_traits, "Sigmar Battle Traits")

    # AoS Faction Editor
    sigmar_factions = ListObjectEditorWidget("Factions", json_data, "sigmarFactions", faction_layout)
    tab_widget.addTab(sigmar_factions, "Sigmar Factions Editor")


class SigmarPlayerDetailsWidget(QWidget):
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

    def __init__(self, json_data: dict, ee):
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
                        wData[key] = wData[key].format(roundNum=i+1, roundIndex=i)
            widgetHelpers.create_json_widgets(tab_layout, json_data, cur_round_data, self.widget_list)
            tab.setLayout(tab_layout)
            left_tabs.addTab(tab, "Round " + str(i+1) + " Scoring")
        left_column.addWidget(left_tabs)

        layout.addLayout(left_column, 4, 0)

        # Right Player column
        right_column = QVBoxLayout()
        right_column.setAlignment(Qt.AlignTop)

        # Right Player active button at the top
        right_active_button = QPushButton("Set Right Player Active")
        right_active_button.clicked.connect(self.right_player_active)
        right_column.addWidget(right_active_button)

        # Main Right Widgets
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
