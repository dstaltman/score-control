import json
import sys

import pydash
from PySide6.QtCore import Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel, QApplication


class TextToJsonWidget(QWidget):
    def __init__(self, label: str, json_blob: dict, json_location: str, data_type=str, reset_value=None):
        QWidget.__init__(self)

        self.jsonLocation = json_location
        self.jsonBlob = json_blob
        self.text = ""
        self.dataType = data_type
        self.reset_value = reset_value

        layout = QHBoxLayout()
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
        if isinstance(self.jsonBlob, type(None)):
            self.textBox.setText('')
            self.setEnabled(False)
            return
        else:
            self.setEnabled(True)

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

    def set_data(self, json_data):
        self.jsonBlob = json_data
        self.read_blob_contents()

    def reset_data(self):
        if self.reset_value is None:
            return

        assert(type(self.reset_value) is str)

        self.textBox.setText(self.reset_value)
        self.text_changed(self.reset_value)

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
    data = {
        "playerName": "name"
    }

    # Window
    window = TextToJsonWidget("Left player", data, 'playerName', int)

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
