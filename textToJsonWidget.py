import json
import sys

import pydash
from PySide6.QtCore import Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QApplication


class TextToJsonWidget(QWidget):
    def __init__(self, label: str, json_blob: dict, json_location: str, data_type=str):
        QWidget.__init__(self)

        self.jsonLocation = json_location
        self.jsonBlob = json_blob
        self.text = ""
        self.dataType = data_type

        layout = QVBoxLayout()
        self.labelWidget = QLabel(label)
        layout.addWidget(self.labelWidget)
        self.textBox = QLineEdit()
        self.textBox.textEdited.connect(self.text_changed)
        layout.addWidget(self.textBox)

        # If we are expecting an integer, set the box to int and give
        # it a validator
        if self.dataType == int:
            validator = QIntValidator(-1, 999, self)
            self.textBox.setValidator(validator)

        self.setLayout(layout)
        self.read_blob_contents()

    def read_blob_contents(self):
        val = pydash.get(self.jsonBlob, self.jsonLocation)

        # No matter the dataType we get input, output as a string
        # We will error if it is not int, string, or empty though
        # This protects us from dict or array
        if val is None:
            self.text = ""
        elif type(val) is int:
            self.text = str(val)
        elif type(val) is str:
            self.text = val
        else:
            raise TypeError('Expected no value, int, or string')

        self.textBox.setText(self.text)

    @Slot()
    def text_changed(self, text):
        self.text = text

        # Convert to int if needed. This will not catch exceptions
        # as we are relying on the TextLine validator
        val = self.text
        if self.dataType == int:
            val = int(self.text)

        pydash.set_(self.jsonBlob, self.jsonLocation, val)


if __name__ == "__main__":
    # QT application
    app = QApplication(sys.argv)

    # load the json
    with open('testdata.json', 'r') as read_file:
        data = json.load(read_file)

    # Widget

    # int test case in a round
    # window = TextToJsonWidget("Left Player", data, 'left.aosRoundScores[0].primaryScore', int)

    # string test case
    # window = TextToJsonWidget("Left player", data, 'left.playerName')

    # test case where we have no pre-existing data
    window = TextToJsonWidget("Left player", data, 'left.playerNameAlternate')

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
