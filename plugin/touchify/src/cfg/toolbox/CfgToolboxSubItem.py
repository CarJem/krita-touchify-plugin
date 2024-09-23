from ...ext.JsonExtensions import JsonExtensions as Extensions

class CfgToolboxSubItem:

    name: str = ""
    icon: str = ""

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
    
    def __str__(self):
        return self.name.replace("\n", "\\n")
    
    def propertygrid_ismodel(self):
        return True
    
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