import unittest
from integerWidget import IntegerWidget
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


class IntegerWidgetTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super(IntegerWidgetTestCase, self).setUp()
        if isinstance(QApplication.instance(), type(None)):
            self.app = QApplication()
        else:
            self.app = QApplication.instance()

    def tearDown(self) -> None:
        del self.app
        return super(IntegerWidgetTestCase, self).tearDown()

    def testButtons(self):
        data = {"index": 10}
        widget = IntegerWidget("integer", data, "index")
        self.assertEqual("integer", widget.label.text())

        QTest.mouseClick(widget.minusFiveBtn, Qt.LeftButton)
        self.assertEqual("5", widget.textBox.text())
        self.assertEqual(5, widget.jsonBlob["index"])

        QTest.mouseClick(widget.minusOneBtn, Qt.LeftButton)
        self.assertEqual(4, widget.jsonBlob["index"])

        QTest.mouseClick(widget.addFiveBtn, Qt.LeftButton)
        self.assertEqual(9, widget.jsonBlob["index"])

        QTest.mouseClick(widget.addOneBtn, Qt.LeftButton)
        self.assertEqual(10, widget.jsonBlob["index"])

    def testTextInputs(self):
        data = {"index": 10}
        widget = IntegerWidget("integer", data, "index")

        # Nothing changes when numbers entered
        QTest.keyClicks(widget.textBox, "hello")
        self.assertEqual("10", widget.textBox.text())

        # clear with backspace then enter a number
        QTest.keyClicks(widget.textBox, "\b\b5")
        self.assertEqual("5", widget.textBox.text())
        self.assertEqual(5, widget.jsonBlob["index"])

        # clear with backspace then enter a negative number
        # negative will fail
        QTest.keyClicks(widget.textBox, "\b\b\b-3")
        self.assertEqual("3", widget.textBox.text())
        self.assertEqual(3, widget.jsonBlob["index"])

        # clear with backspace then enter a 4 digit number
        # will only have 3 numbers
        QTest.keyClicks(widget.textBox, "\b\b\b4444")
        self.assertEqual("444", widget.textBox.text())
        self.assertEqual(444, widget.jsonBlob["index"])

    def test_new_value(self):
        data = {}
        widget = IntegerWidget("integer", data, "index")

        # empty should create with a 0 value
        self.assertEqual("0", widget.textBox.text())
        self.assertEqual(0, widget.jsonBlob["index"])

        # set a number and it should be set in box
        QTest.keyClicks(widget.textBox, "0010")
        self.assertEqual("00010", widget.textBox.text())
        self.assertEqual(10, widget.jsonBlob["index"])

    def test_error_value(self):
        data = {"index": "string"}
        with self.assertRaises(TypeError):
            IntegerWidget("name", data, "index")

    def test_none_value(self):
        widget = IntegerWidget("int", None, "index")

        # test empty and disabled
        self.assertEqual("", widget.textBox.text())
        self.assertFalse(widget.isEnabled())

        # Add some data
        data = {"index": 10}
        widget.set_data(data)
        self.assertEqual("10", widget.textBox.text())
        self.assertTrue(widget.isEnabled())

        widget.set_data(None)
        self.assertEqual("", widget.textBox.text())
        self.assertFalse(widget.isEnabled())

    def test_reset_data(self):
        data = {"index": 10}
        widget = IntegerWidget("integer", data, "index", reset_value=0)

        self.assertEqual("10", widget.textBox.text())
        self.assertTrue(widget.isEnabled())

        widget.reset_data()

        self.assertEqual("0", widget.textBox.text())
        self.assertEqual(0, widget.jsonBlob["index"])



if __name__ == '__main__':
    unittest.main()
