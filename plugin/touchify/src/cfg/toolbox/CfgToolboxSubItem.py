from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions

class CfgToolboxSubItem:

    def __defaults__(self):
        name: str = ""
        icon: str = ""

        json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)
    
    def __str__(self):
        return self.name.replace("\n", "\\n")
    
    def propertygrid_ismodel(self):
        return True
    

    def propertygrid_sorted(self):
        return [
            "name",
            "icon"
        ]
    
    def propertygrid_labels(self):
        labels = {}
        labels["name"] = "Action ID"
        labels["icon"] = "Custom Icon"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["name"] = {"type": "action_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions