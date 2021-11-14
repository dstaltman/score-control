from comboBoxWidget import ComboBoxWidget
from PySide6.QtWidgets import QApplication


class TestComboBoxWidget:
    app = None
    output = {'key': 'Item 3'}
    output_location = 'key'
    input_items = {
        'inputs': [
            {'name': 'Item 1', 'type': 'A'},
            {'name': 'Item 2', 'type': 'B'},
            {'name': 'Item 3', 'type': 'A'},
            {'name': 'Item 4', 'type': 'A'},
        ]
    }
    input_location = 'inputs'

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
        def filter_items(item_data):
            return True

        widget = ComboBoxWidget("label", self.output, self.output_location, self.input_items, self.input_location,
                                filter_items)
        assert widget.label.text() == "label"

        # assert saved data
        assert widget.out_json_data == self.output
        assert widget.out_json_location == self.output_location
        assert widget.item_json_data == self.input_items
        assert widget.item_json_location == self.input_location
        assert widget.filter_func == filter_items

        # Items
        assert widget.comboBox.count() == 4
        assert widget.comboBox.currentIndex() == 2

    def test_filter(self):
        def filter_items(item_data):
            return item_data['type'] == 'A'

        widget = ComboBoxWidget("label", self.output, self.output_location, self.input_items, self.input_location,
                                filter_items)

        # Items
        assert widget.comboBox.count() == 3
        assert widget.comboBox.currentIndex() == 1

        # Test a filter that accepts all
        def no_filter(item_data):
            return True

        widget.set_filter_function(no_filter)

        assert widget.comboBox.count() == 4
        assert widget.comboBox.currentIndex() == 2

        # Test a filter that results in no valid selection
        # This picks the first item in the list
        widget.set_type_filter('B')

        assert widget.comboBox.count() == 1
        assert widget.comboBox.currentIndex() == 0

    def test_empty_out_data(self):
        test_output = {}
        widget = ComboBoxWidget("label", test_output, self.output_location, self.input_items, self.input_location)

        # When we have no data, set the data to the first item in the list
        assert widget.comboBox.currentText() == 'Item 1'
        assert widget.current_item == 'Item 1'

    def test_reset_button(self):
        widget = ComboBoxWidget("label", self.output, self.output_location, self.input_items, self.input_location,
                                reset_value='Item 1')

        # We have 3 selected now
        assert widget.comboBox.currentText() == 'Item 3'
        assert widget.current_item == 'Item 3'

        # Reset data
        widget.reset_data()

        assert widget.current_item == 'Item 1'
        assert widget.comboBox.currentText() == 'Item 1'

        # don't change value if reset value is invalid
        widget.reset_value = 'Item 5'

        assert widget.current_item == 'Item 1'
        assert widget.comboBox.currentText() == 'Item 1'
