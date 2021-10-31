import sys
from collections.abc import Callable

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QApplication, QFileDialog


class LoadFileWidget(QWidget):
    def __init__(self, label: str, file_picked_func: Callable[[str], None]):
        super().__init__()
        self.label = label
        self.fileName = None
        self.file_picked_callback = file_picked_func

        layout = QHBoxLayout()

        layout.addWidget(QLabel(self.label))
        self.pick_file_button = QPushButton("Select File")
        self.pick_file_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.pick_file_button)

        self.setLayout(layout)

    @Slot()
    def open_file_dialog(self):
        open_file_data = QFileDialog.getOpenFileName(self, "File", "Open File", "JSON Files (*.json)")
        self.fileName = open_file_data[0]
        if isinstance(self.fileName, type(None)):
            return
        if not isinstance(self.file_picked_callback, type(None)):
            self.file_picked_callback(self.fileName)


def do_nothing(file_string: str):
    print(file_string)


if __name__ == "__main__":
    # QT application
    app = QApplication(sys.argv)

    # Widget
    window = LoadFileWidget("pick a file, any file", do_nothing)

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
