import sys
import pydash

from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel, QApplication
from PySide6.QtCore import Slot


class ComboBoxWidget(QWidget):
    comboBox = None
    item_json_data = None
    item_json_location = None
    out_json_data = None
    out_json_location = None
    num_items = 0
    filter_func = None

    def __init__(self, label: str, out_json_data: dict, out_json_location: str, item_json_data: dict,
                 item_json_location: str, filter_func=None, type_filter=None):
        QWidget.__init__(self)

        self.item_json_data = item_json_data
        self.item_json_location = item_json_location
        self.out_json_data = out_json_data
        self.out_json_location = out_json_location
        self.filter_func = filter_func
        self.current_item = pydash.get(self.out_json_data, self.out_json_location)
        self.type_filter = type_filter
        if isinstance(self.type_filter, str):
            self.set_type_filter(self.type_filter)

        # Assert on requirements
        assert isinstance(self.item_json_location, str)
        assert isinstance(self.out_json_location, str)

        # Begin layout
        layout = QHBoxLayout()

        # Label
        self.label = QLabel(label)
        layout.addWidget(self.label)

        # Combo box
        self.comboBox = QComboBox()
        self.add_items()
        self.comboBox.activated.connect(self.selection_changed)
        layout.addWidget(self.comboBox)

        # Set the layout to active
        self.setLayout(layout)

    @Slot()
    def selection_changed(self):
        self.current_item = self.comboBox.currentText()
        pydash.set_(self.out_json_data, self.out_json_location, self.comboBox.currentText())

    def set_data(self, out_json_data):
        self.out_json_data = out_json_data
        self.current_item = pydash.get(self.out_json_data, self.out_json_location)
        self.reset_items()

    def set_type_filter(self, type_filter):
        self.set_filter_function(lambda i: 'type' in i and i['type'] == type_filter)

    def set_filter_function(self, filter_func):
        self.filter_func = filter_func
        self.reset_items()

    def reset_items(self):
        if isinstance(self.comboBox, type(None)):
            return
        self.comboBox.clear()
        self.num_items = 0
        self.add_items()

    def set_item_data(self, item_data):
        self.item_json_data = item_data
        self.reset_items()

    def add_items(self):
        if isinstance(self.item_json_data, type(None)) or isinstance(self.item_json_location, type(None)):
            self.setEnabled(False)
            return

        current_item_found = False
        for item in self.item_json_data[self.item_json_location]:
            # Filter out items that our filter dislikes
            if not isinstance(self.filter_func, type(None)):
                if not self.filter_func(item):
                    continue

            # Add Item to the combo box and see if it is the current selection
            self.comboBox.insertItem(self.num_items, item['name'])
            if self.current_item == item['name']:
                self.comboBox.setCurrentIndex(self.num_items)
                current_item_found = True
            self.num_items += 1

        if not current_item_found:
            self.current_item = self.comboBox.currentText()


if __name__ == "__main__":
    # QT application
    app = QApplication(sys.argv)

    # Test Data
    output = {'key': 'Item 3'}
    output_location = 'key'
    input_items = {
        'inputs': [
            {'name': 'Item 1', 'type': 'A'},
            {'name': 'Item 2', 'type': 'B'},
            {'name': 'Item 3', 'type': 'A'},
            {'name': 'Item 4', 'type': 'A'},
        ]
    }
    input_location = 'inputs'

    def test_filter(item_data):
        return item_data['type'] == 'B'

    window = ComboBoxWidget("combo box", output, output_location, input_items, input_location, test_filter)
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
