from ..ext.extensions_json import JsonExtensions as Extensions


class CfgPopupInfo:
    text: str = ""
    action: str = ""
    icon: str = ""


    def propertygrid_labels(self):
        labels = {}
        labels["action"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["text"] = "Display Text"
        return labels

    def create(args):
        obj = CfgPopupInfo()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        return self.text.replace("\n", "\\n")

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["action"] = {"type": "action_selection"}
        return restrictions