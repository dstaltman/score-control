from loadFileWidget import LoadFileWidget
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import Qt


class TestLoadFileWidget:
    @classmethod
    def setup_class(cls):
        if isinstance(QApplication.instance(), type(None)):
            cls.app = QApplication()
        else:
            cls.app = QApplication.instance()

    @classmethod
    def teardown_class(cls):
        del cls.app

    def do_nothing_callback(self, filename):
        return

    def test_create_widget(self):
        widget = LoadFileWidget("label", self.do_nothing_callback)
        assert widget.label == "label"
        assert isinstance(widget.pick_file_button, QPushButton)

    def test_get_file(self, mocker):
        mocker.patch('loadFileWidget.QFileDialog.getOpenFileName', return_value=('file_name.json', 'filetype'))
        widget = LoadFileWidget("label", self.do_nothing_callback)
        QTest.mouseClick(widget.pick_file_button, Qt.LeftButton)
        assert isinstance(widget.fileName, str)
        assert widget.fileName == "file_name.json"

    def test_callback(self, mocker):
        mocker.patch('loadFileWidget.QFileDialog.getOpenFileName', return_value=('file_name.json', 'filetype'))
        m = mocker.Mock()
        widget = LoadFileWidget("label", m)
        QTest.mouseClick(widget.pick_file_button, Qt.LeftButton)
        m.assert_called_once_with('file_name.json')
