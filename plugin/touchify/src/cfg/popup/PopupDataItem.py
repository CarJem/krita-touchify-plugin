from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions


class PopupDataItem:

    def __defaults__(self):
        self.text: str = ""
        self.action: str = ""
        self.icon: str = ""

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)

    def propertygrid_sorted(self):
        return [
            "action",
            "text",
            "icon"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["action"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["text"] = "Display Text"
        return labels

    def __str__(self):
        return self.text.replace("\n", "\\n")

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["action"] = {"type": "action_selection"}
        return restrictions