from textToJsonWidget import TextToJsonWidget
from integerWidget import IntegerWidget
from comboBoxWidget import ComboBoxWidget
from PySide6.QtWidgets import QFrame, QLabel
from PySide6.QtCore import Qt
import pydash


# Creates a lambda to allow for combo box based on data in json
def build_field_test(item_json_location: str, json_blob: dict, dict_json_location: str):
    return lambda item: item_json_location not in item or item[item_json_location] \
                        in [None, "", "None", pydash.get(json_blob, dict_json_location)]


# Makes widgets and adds to passed in layout
#
# json_data is the data passed to each widget to update
# data contains information on how to create the widgets
# Example:
# {
#     'type': <text/integer/combo/separator>,
#     'label': <widget label>,
#     'jsonLocation': <whereToUpdate>,
#     'itemsLocation': <whereItemsLive>, -- combo
#     'itemFilterType', <typeRequired>, -- combo
#     'resetValue': <value>, -- Optional
# }
def create_json_widgets(layout, json_data: dict, data=None, widget_list: list = None):
    use_list = isinstance(widget_list, list)
    for mainWidgetData in data:
        reset_value = None
        if "resetValue" in mainWidgetData:
            reset_value = mainWidgetData["resetValue"]
        if mainWidgetData["type"] == "text":
            text_line_widget = TextToJsonWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"],
                                                reset_value=reset_value)
            layout.addWidget(text_line_widget)
            if use_list:
                widget_list.append(text_line_widget)

        elif mainWidgetData["type"] == "integer":
            int_widget = IntegerWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"],
                                       reset_value=reset_value)
            layout.addWidget(int_widget)
            if use_list:
                widget_list.append(int_widget)

        elif mainWidgetData["type"] == "combo":
            type_filter = None
            if "itemFilterType" in mainWidgetData:
                type_filter = mainWidgetData["itemFilterType"]
            filterFunc = None
            if "filterFunc" in mainWidgetData:
                filterFunc = mainWidgetData["filterFunc"]
            combo_widget = ComboBoxWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"],
                                          json_data, mainWidgetData["itemsLocation"], type_filter=type_filter,
                                          reset_value=reset_value, filter_func=filterFunc)
            layout.addWidget(combo_widget)
            if use_list:
                widget_list.append(combo_widget)

        elif mainWidgetData["type"] == "separator":
            frame = QLabel(mainWidgetData["label"])
            frame.setAlignment(Qt.AlignCenter)
            frame.setFrameStyle(QFrame.Panel | QFrame.Plain)
            frame.setLineWidth(2)

            def set_data_func():
                pass
            frame.set_data = set_data_func

            layout.addWidget(frame)
