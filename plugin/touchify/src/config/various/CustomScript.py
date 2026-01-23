from jemlib.alib_vaporjem.extensions.file_extensions import FileExtensions
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class CustomScript:

    def __defaults__(self):
        self.script_name: str = "New Script"
        self.script_code: str = ""

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [])

    def __str__(self):
        return self.script_name.replace("\n", "\\n")

    def getFileName(self):
        return FileExtensions.fileStringify(self.script_name)

       
    def propertygrid_sorted(self):
        return [
            "script_name",
            "script_code"
        ]

    def propertygrid_hidden(self):
        result = []
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["script_name"] = "Script Name"
        labels["script_code"] = "Code"
        return labels

    def propertygrid_restrictions(self):   
        restrictions = {}
        restrictions["script_code"]  = DataConstraints.strMod(DataConstraints.StrMod.PythonEditor)
        return restrictions