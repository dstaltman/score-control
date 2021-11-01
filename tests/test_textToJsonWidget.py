import unittest
from textToJsonWidget import TextToJsonWidget
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication


class TestTextToJsonWidget(unittest.TestCase):
    def setUp(self) -> None:
        super(TestTextToJsonWidget, self).setUp()
        if isinstance(QApplication.instance(), type(None)):
            self.app = QApplication()
        else:
            self.app = QApplication.instance()
        self._label = "label"

    def tearDown(self) -> None:
        del self.app
        return super(TestTextToJsonWidget, self).tearDown()

    def test_update_string_value(self):
        # setup for str based widget
        index = "index"
        value = "value"
        data = {index: value}
        widget = TextToJsonWidget(self._label, data, index)

        # test setup of str widget
        self.assertEqual(self._label, widget.labelWidget.text())
        self.assertEqual(data, widget.jsonBlob)
        self.assertEqual(str, widget.dataType)
        self.assertEqual(value, widget.textBox.text())

        # typing in the text box will append to existing string
        QTest.keyClicks(widget.textBox, "new")
        self.assertEqual("valuenew", widget.textBox.text())
        self.assertEqual({index: "valuenew"}, widget.jsonBlob)

    def test_update_int_value(self):
        # setup for int based widget
        index = "index"
        value = 1
        data = {index: value}
        widget = TextToJsonWidget(self._label, data, index, int)

        # test setup of int widget
        self.assertEqual(self._label, widget.labelWidget.text())
        self.assertEqual(data, widget.jsonBlob)
        self.assertEqual(int, widget.dataType, int)
        self.assertEqual(str(value), widget.textBox.text())

        # Using a string when a number will not change text
        QTest.keyClicks(widget.textBox, "k")
        self.assertEqual(str(value), widget.textBox.text())
        # using a number will change the string text and the json int value
        QTest.keyClicks(widget.textBox, "1")
        self.assertEqual(str(value) + "1", widget.textBox.text())
        self.assertEqual({index: 11}, widget.jsonBlob)

    def test_new_string_value(self):
        # setup for str based widget where value is added
        index = "newIndex"
        data = {}
        widget = TextToJsonWidget(self._label, data, index)

        # test setup of new str widget
        self.assertEqual(widget.labelWidget.text(), self._label)
        self.assertEqual(widget.jsonBlob, data)
        self.assertEqual(widget.dataType, str)
        self.assertEqual(widget.textBox.text(), "")

        # typing in the text box will create the key-value pair based on input
        QTest.keyClicks(widget.textBox, "new")
        self.assertEqual("new", widget.textBox.text())
        self.assertEqual({index: "new"}, widget.jsonBlob)


if __name__ == '__main__':
    unittest.main()
