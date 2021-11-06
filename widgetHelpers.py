from textToJsonWidget import TextToJsonWidget
from integerWidget import IntegerWidget
from comboBoxWidget import ComboBoxWidget
from PySide6.QtWidgets import QFrame, QLabel
from PySide6.QtCore import Qt


# Makes widgets and adds to passed in layout
#
# json_data is the data passed to each widget to update
# data contains information on how to create the widgets
# Example:
# {
#     'type': <textLineWidget/integerWidget/comboWidget/separator>,
#     'label': <widget label>,
#     'jsonLocation': <whereToUpdate>,
#     'itemsLocation': <whereItemsLive>, -- comboWidget
#     'itemFilterType', <typeRequired>, -- comboWidget
# }
def create_json_widgets(layout, json_data: dict, data=None, widget_list: list = None):
    use_list = isinstance(widget_list, list)
    for mainWidgetData in data:
        if mainWidgetData["type"] == "textLineWidget":
            textLineWidget = TextToJsonWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(textLineWidget)
            if use_list:
                widget_list.append(textLineWidget)

        elif mainWidgetData["type"] == "integerWidget":
            intWidget = IntegerWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(intWidget)
            if use_list:
                widget_list.append(intWidget)

        elif mainWidgetData["type"] == "comboWidget":
            type_filter = None
            if "itemFilterType" in mainWidgetData:
                type_filter = mainWidgetData["itemFilterType"]
            comboWidget = ComboBoxWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"],
                                         json_data, mainWidgetData["itemsLocation"], type_filter=type_filter)
            layout.addWidget(comboWidget)
            if use_list:
                widget_list.append(comboWidget)

        elif mainWidgetData["type"] == "separator":
            frame = QLabel(mainWidgetData["label"])
            frame.setAlignment(Qt.AlignCenter)
            frame.setFrameStyle(QFrame.Panel | QFrame.Plain)
            frame.setLineWidth(2)
            layout.addWidget(frame)
