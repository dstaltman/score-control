import copy
import json
import sys
import pydash


# Manages files by opening a json file and keeping in memory.
# Other modules use a reference to the json data that is
# returned by this module. When asked to save, this will check
# if the json data is dirty before dumping it out.
class FileManager:
    def __init__(self, file_path):
        self._filePath = file_path

        # load the json
        with open(self._filePath, 'r') as read_file:
            self.jsonData = json.load(read_file)

        self.jsonOld = copy.deepcopy(self.jsonData)

    # If the file is dirty, we write it out
    def write_file(self):
        if self.jsonOld != self.jsonData:
            self.jsonOld = copy.deepcopy(self.jsonData)

            with open(self._filePath, 'w') as read_file:
                read_file.write(json.dumps(self.jsonData, sort_keys=True, indent=4))

    def get_json_data(self):
        return self.jsonData


if __name__ == "__main__":
    fileMan = FileManager('testdata.json')
    print(fileMan.get_json_data())
