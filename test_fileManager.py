import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock
from fileManager import FileManager
import pydash


class FileManagerTest(unittest.TestCase):

    @patch('fileManager.path.isfile')
    def test_fileManager(self, mock_isfile_call):
        mock_isfile_call.return_value = MagicMock(True)
        testDataObj = {
            'left': {
                'playerName': 'Dru'
            }
        }
        updateDataObj = {
            'left': {
                'playerName': 'Dru',
                'armyName': 'elf'
            }
        }
        testData = '{"left": {"playerName": "Dru" }}'
        updateData = '{\n    "left": {\n        "armyName": "elf",\n        "playerName": "Dru"\n    }\n}'
        open_mock = mock_open(
            read_data=testData
        )
        with patch("fileManager.open", open_mock, create=True):
            # create a file manager, update the data, write it out
            fileMan = FileManager('test-file.json')
            data = fileMan.get_json_data()
            pydash.set_(data, 'left.armyName', 'elf')
            fileMan.write_file()

        # Check with the mock that all was correct
        open_mock.assert_called_with('test-file.json', 'w')
        self.assertNotEqual(fileMan.jsonData, testDataObj)
        self.assertEqual(fileMan.jsonData, updateDataObj)
        handle = open_mock()
        handle.write.assert_called_once()
        handle.write.assert_called_with(updateData)

    def test_missingFile(self):
        m = Mock()
        with patch("fileManager.open", m):
            fileMan = FileManager("missing-file.omg")
            fileMan.write_file()
        self.assertEqual(fileMan.is_valid(), False)
        handle = m()
        handle.open.assert_not_called()
        handle.write.assert_not_called()

    @patch('fileManager.path.isfile')
    def test_wrongFileType(self, mock_isfile_call):
        mock_isfile_call.return_value = MagicMock(True)
        fileData = "This is not a json file"
        open_mock = mock_open(
            read_data=fileData
        )
        with patch("fileManager.open", open_mock, create=True):
            fileMan = FileManager('test-file.txt')
            data = fileMan.get_json_data()
            if isinstance(data, dict):
                pydash.set_(data, 'index', 'value')
            fileMan.write_file()

        self.assertEqual(fileMan.is_valid(), False)
        handle = open_mock()
        handle.write.assert_not_called()


if __name__ == '__main__':
    unittest.main()
