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
        self._strIndex = "index"
        self._strValue = "value"
        self._strData = {self._strIndex: self._strValue}
        self.textWidgetString = TextToJsonWidget(self._label, self._strData, self._strIndex)

        # test setup of str widget
        self.assertEqual(self.textWidgetString.labelWidget.text(), self._label)
        self.assertEqual(self.textWidgetString.jsonBlob, self._strData)
        self.assertEqual(self.textWidgetString.dataType, str)
        self.assertEqual(self.textWidgetString.textBox.text(), self._strValue)

        # typing in the text box will append to existing string
        QTest.keyClicks(self.textWidgetString.textBox, "new")
        self.assertEqual("valuenew", self.textWidgetString.textBox.text())
        self.assertEqual({self._strIndex: "valuenew"}, self.textWidgetString.jsonBlob)

    def test_update_int_value(self):
        # setup for int based widget
        self._intIndex = "index"
        self._intValue = 1
        self._intData = {self._intIndex: self._intValue}
        self.textWidgetInt = TextToJsonWidget(self._label, self._intData, self._intIndex, int)

        # test setup of int widget
        self.assertEqual(self.textWidgetInt.labelWidget.text(), self._label)
        self.assertEqual(self.textWidgetInt.jsonBlob, self._intData)
        self.assertEqual(self.textWidgetInt.dataType, int)
        self.assertEqual(self.textWidgetInt.textBox.text(), str(self._intValue))

        # Using a string when a number will not change text
        QTest.keyClicks(self.textWidgetInt.textBox, "k")
        self.assertEqual(str(self._intValue), self.textWidgetInt.textBox.text())
        # using a number will chage the string text and the json int value
        QTest.keyClicks(self.textWidgetInt.textBox, "1")
        self.assertEqual(str(self._intValue) + "1", self.textWidgetInt.textBox.text())
        self.assertEqual({self._intIndex: 11}, self.textWidgetInt.jsonBlob)

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
