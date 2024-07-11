from ..ext.extensions_json import JsonExtensions as Extensions


class CfgWorkspace:
    display_name: str = ""
    id: str = ""
    icon: str = ""

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Workspace ID"
        labels["display_name"] = "Display Name"
        labels["icon"] = "Preview Icon"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions