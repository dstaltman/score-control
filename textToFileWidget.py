import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QApplication
from PySide6.QtCore import Slot
from pathlib import Path


class TextToFileWidget(QWidget):
    def __init__(self, file, label):
        super().__init__()

        self.fileName = file
        self.text = ""

        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))
        self.textBox = QLineEdit()
        self.textBox.textEdited.connect(self.text_changed)
        layout.addWidget(self.textBox)

        self.setLayout(layout)
        self.read_file_contents()

    def read_file_contents(self):
        # Touch the file to ensure it exists for reading later
        file = Path(self.fileName)
        file.touch(exist_ok=True)

        with open(self.fileName, encoding='utf-8') as f:
            self.text = f.read()
            print("Reading File - " + self.text)
            self.textBox.setText(self.text)

    @Slot()
    def text_changed(self, text):
        with open(self.fileName, "w") as f:
            self.text = text
            f.write(self.text)


if __name__ == "__main__":
    # QT application
    app = QApplication(sys.argv)

    # Widget

    window = TextToFileWidget("C:\\StreamTextFiles\\LeftPlayerName.txt", "Left Player")
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
