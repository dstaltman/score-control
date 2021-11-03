import sys

import pydash
from PySide6.QtCore import Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QApplication


# Widget that will control integer values in a json blob.
#
# Can control the integer with a text box or buttons to increment and decrement.
class IntegerWidget(QWidget):
    def __init__(self, label: str, json_blob: dict, json_location: str):
        super().__init__()
        self.label = label
        self.jsonBlob = json_blob
        self.jsonLocation = json_location

        layout = QHBoxLayout()
        self.label = QLabel(label)
        layout.addWidget(self.label)

        # Number and buttons
        # Button with -5
        self.minusFiveBtn = QPushButton("-5")
        self.minusFiveBtn.clicked.connect(self.minus_five_pressed)
        layout.addWidget(self.minusFiveBtn)

        # Button with -1
        self.minusOneBtn = QPushButton("-1")
        self.minusOneBtn.clicked.connect(self.minus_one_pressed)
        layout.addWidget(self.minusOneBtn)

        # The Text box with the integer
        self.textBox = QLineEdit("")
        self.textBox.textEdited.connect(self.text_changed)
        validator = QIntValidator(0, 100, self)
        self.textBox.setValidator(validator)
        layout.addWidget(self.textBox)

        # Button with +1
        self.addOneBtn = QPushButton("+1")
        self.addOneBtn.clicked.connect(self.add_one_pressed)
        layout.addWidget(self.addOneBtn)

        # Button with +5
        self.addFiveBtn = QPushButton("+5")
        self.addFiveBtn.clicked.connect(self.add_five_pressed)
        layout.addWidget(self.addFiveBtn)

        self.setLayout(layout)

        # Get initial value
        self.read_value()

    def read_value(self):
        if isinstance(self.jsonBlob, type(None)):
            self.textBox.setText("")
            self.setEnabled(False)
            return
        else:
            self.setEnabled(True)
        val = pydash.get(self.jsonBlob, self.jsonLocation)

        # No matter the dataType we get input, output as a string
        # We will error if it is not int or empty though
        # This protects us from dict or array
        setJsonValue = False
        if val is None:
            val = "0"
            setJsonValue = True
        elif type(val) is int:
            val = str(val)
        else:
            raise TypeError('Expected no value, int, or string')

        self.textBox.setText(val)
        if setJsonValue:
            self.set_json_value()

    def set_data(self, json_data):
        self.jsonBlob = json_data
        self.read_value()

    def change_value(self, add: int):
        # Convert to int. This will not catch exceptions
        # as we are relying on the TextLine validator
        # truth is the text line value
        val = int(self.textBox.text())
        val += add
        self.textBox.setText(str(val))
        self.set_json_value()

    def set_json_value(self):
        # Convert to int. This will not catch exceptions
        # as we are relying on the TextLine validator
        # truth is the text line value
        val = int(self.textBox.text())
        pydash.set_(self.jsonBlob, self.jsonLocation, val)

    @Slot()
    def minus_one_pressed(self):
        self.change_value(-1)

    @Slot()
    def minus_five_pressed(self):
        self.change_value(-5)

    @Slot()
    def add_five_pressed(self):
        self.change_value(5)

    @Slot()
    def add_one_pressed(self):
        self.change_value(1)

    @Slot()
    def text_changed(self, text):
        # Convert to int. This will not catch exceptions
        # as we are relying on the TextLine validator
        if len(text) > 0:
            val = int(text)
        else:
            val = 0

        pydash.set_(self.jsonBlob, self.jsonLocation, val)


if __name__ == "__main__":
    # QT application
    app = QApplication(sys.argv)

    # test json data
    data = {"index": 10}

    # Widget
    window = IntegerWidget("Integer", data, 'index')

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
