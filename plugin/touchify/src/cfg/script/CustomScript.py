from krita import *
from PyQt5.QtCore import *
from touchify.src.components.python.file_extensions import FileExtensions
from touchify.src.components.krita.settings import *
from touchify.src.components.krita.extensions import *
from touchify.src.components.python.json_extensions import JsonExtensions as Extensions
from touchify.src.components.touchify.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class CustomScript:

    def __defaults__(self):
        self.script_name: str = "New Script"
        self.script_code: str = ""

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args, [])

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
        restrictions["script_code"]  = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.PythonEdtior)
        return restrictions