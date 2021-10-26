import unittest
from unittest.mock import patch, mock_open
import fileManager
import pydash


class FileManagerTest(unittest.TestCase):
    def test_fileManager(self):
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
            fileMan = fileManager.FileManager('test-file.json')
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


if __name__ == '__main__':
    unittest.main()
