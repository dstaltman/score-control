import sys

import pydash
import widgetHelpers
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QApplication, \
    QSizePolicy, QFrame, QMessageBox


# Widget that displays a list of objects to be edited
#
# List will support new, edit, delete functionality. The widget itself
# is handed a list of objects that are all string types to be outputted
# in a JSON file.
class ListObjectEditorWidget(QWidget):
    item_lines = []
    edit_widgets = []
    message_box = None
    active_object = None

    def __init__(self, title: str, edit_data: dict, data_location: str, editor_layout: list):
        super().__init__()

        self.item_lines = []
        self.edit_widgets = []
        self.message_box = None
        self.active_object = None

        self.layout = QHBoxLayout()

        # Left box with list of all objects to edit
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignTop)

        self.data = edit_data
        self.data_location = data_location

        # If the data doesn't exist in the dictionary, create it
        assert isinstance(self.data, dict)
        if self.data_location not in self.data:
            self.data[self.data_location] = []
        assert isinstance(self.data[self.data_location], list)

        self.data_list_label = QLabel(title)
        self.data_list_label.setAlignment(Qt.AlignHCenter)
        self.left_layout.addWidget(self.data_list_label)

        self.add_object_button = QPushButton("Add Item")
        self.add_object_button.clicked.connect(self.add_object)
        self.left_layout.addWidget(self.add_object_button)

        self.layout.addLayout(self.left_layout)

        # Right box that contains all the fields to edit in an object instance
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignTop)

        self.editor_label = (QLabel("Data Editor"))
        self.editor_label.setAlignment(Qt.AlignHCenter)
        self.right_layout.addWidget(self.editor_label)

        # Add widgets for the edit pane
        name_widget_data = {
            'type': 'text',
            'label': 'Object Name',
            'jsonLocation': 'name'
        }
        editor_layout.insert(0, name_widget_data)
        widgetHelpers.create_json_widgets(self.right_layout, self.data, editor_layout, self.edit_widgets)

        self.layout.addLayout(self.right_layout)

        # Initialize data and finalize the widget
        self.populate_editor_data()

        self.setLayout(self.layout)

    def populate_editor_data(self):
        self.item_lines.clear()
        for obj in self.data[self.data_location]:
            self.add_data_line(obj)

    def add_object(self):
        new_object = {'name': 'New Object'}
        self.data[self.data_location].append(new_object)
        self.add_data_line(new_object)
        self.set_edit_object(new_object)

    def set_edit_object(self, object_data):
        self.active_object = object_data
        for w in self.edit_widgets:
            w.set_data(self.active_object)

    def add_data_line(self, line_data):
        # Frame Widget for the object
        line_frame = QFrame()
        line_frame.setFrameStyle(QFrame.Panel | QFrame.Plain)
        line_frame.setLineWidth(1)
        line_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        line_frame.object_data = line_data

        # Layout for the widget
        line_layout = QHBoxLayout()
        line_layout.setAlignment(Qt.AlignTop)

        # Object Name
        line_layout.addWidget(QLabel(line_data['name']))

        # Edit button
        edit_button = QPushButton("Edit")
        edit_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        edit_button.resize(40, edit_button.sizeHint().height())
        edit_button.clicked.connect(lambda x: self.edit_data_button(line_frame))
        line_layout.addWidget(edit_button)
        line_frame.edit_button = edit_button

        # delete button
        del_button = QPushButton("Delete")
        del_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        del_button.resize(40, del_button.sizeHint().height())
        del_button.clicked.connect(lambda x: self.delete_data_button(line_frame))
        line_layout.addWidget(del_button)
        line_frame.del_button = del_button

        # final setup of layout and widget information
        line_frame.setLayout(line_layout)
        self.left_layout.addWidget(line_frame)
        self.item_lines.append(line_frame)

    @Slot()
    def edit_data_button(self, arg):
        self.set_edit_object(arg.object_data)

    @Slot()
    def delete_data_button(self, arg):
        msg_box = QMessageBox()
        msg_box.setText("Are you sure you would like to delete " + arg.object_data['name'] + "?")
        msg_box.setInformativeText("This cannot be undone")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        ret = msg_box.exec()
        self.message_box = msg_box

        if ret == QMessageBox.Yes:
            self.message_box = None
            self.confirm_delete(arg)
        else:
            self.message_box = None

    @Slot()
    def confirm_delete(self, arg):
        self.left_layout.removeWidget(arg)
        self.item_lines.remove(arg)
        arg.hide()
        pydash.remove(self.data[self.data_location], lambda x: x['name'] == arg.object_data['name'])


if __name__ == "__main__":
    # QT application
    app = QApplication(sys.argv)

    # test json data
    test_data = {"index": [
        {'name': 'ItemName', 'textValue': 'text text', 'intValue': 111},
        {'name': 'OtherItem', 'textValue': 'other text', 'intValue': 222}
    ]}

    # layout for editor pane
    test_editor_layout = [
        {
            'type': 'text',
            'label': 'text widget',
            'jsonLocation': 'textValue'
        },
        {
            'type': 'integer',
            'label': 'integer widget',
            'jsonLocation': 'intValue'
        }
    ]

    # Widget
    window = ListObjectEditorWidget("editor", test_data, "index", test_editor_layout)

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
