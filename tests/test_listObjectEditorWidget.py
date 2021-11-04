from listObjectEditorWidget import ListObjectEditorWidget
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QTimer


class TestListObjectEditorWidget:
    app = None
    editor_layout = [
        {'type': 'textLineWidget', 'label': 'text widget', 'jsonLocation': 'textValue'},
        {'type': 'integerWidget', 'label': 'integer widget', 'jsonLocation': 'intValue'}
    ]
    test_data = {"key": [
        {"name": "Item Name 1", 'textValue': 'TEXT TEXT TEXT', 'intValue': 111}
    ]}
    location = "key"

    @classmethod
    def setup_class(cls):
        if isinstance(QApplication.instance(), type(None)):
            cls.app = QApplication()
        else:
            cls.app = QApplication.instance()

    @classmethod
    def teardown_class(cls):
        del cls.app

    def test_init(self):
        data = {"key": []}
        location = "key"
        widget = ListObjectEditorWidget("title", data, location, [])
        assert widget.data_list_label.text() == "title"
        assert widget.data == data
        assert widget.data_location == location

    def test_edit_creation(self):
        widget = ListObjectEditorWidget("title", self.test_data, self.location, self.editor_layout)
        assert len(widget.edit_widgets) == 2

        assert isinstance(widget.active_object, type(None))
        QTest.mouseClick(widget.item_lines[0].edit_button, Qt.LeftButton)
        assert not isinstance(widget.active_object, type(None))

    def test_populate_data(self):
        data = {"key": [
            {"name": "Item Name 1"}
        ]}
        location = "key"
        widget = ListObjectEditorWidget("title", data, location, [])
        assert len(widget.item_lines) == 1

        data = {"key": [
            {"name": "Item Name 1"},
            {"name": "Item Name 2"}
        ]}
        widget = ListObjectEditorWidget("title", data, location, [])
        assert len(widget.item_lines) == 2
