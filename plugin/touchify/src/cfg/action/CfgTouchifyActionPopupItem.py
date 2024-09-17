from ...ext.JsonExtensions import JsonExtensions as Extensions


class CfgTouchifyActionPopupItem:
    text: str = ""
    action: str = ""
    icon: str = ""


    def propertygrid_labels(self):
        labels = {}
        labels["action"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["text"] = "Display Text"
        return labels

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def __str__(self):
        return self.text.replace("\n", "\\n")

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["action"] = {"type": "action_selection"}
        return restrictions