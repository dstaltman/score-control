from textToJsonWidget import TextToJsonWidget
from integerWidget import IntegerWidget


def create_json_widgets(layout, json_data: dict, data=None):
    for mainWidgetData in data:
        if mainWidgetData["type"] == "textLineWidget":
            textLineWidget = TextToJsonWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(textLineWidget)
        elif mainWidgetData["type"] == "integerWidget":
            intWidget = IntegerWidget(mainWidgetData["label"], json_data, mainWidgetData["jsonLocation"])
            layout.addWidget(intWidget)
