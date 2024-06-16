from ..ext.extensions import Extensions


class CfgWorkspace:
    display_name: str = ""
    id: str = ""
    icon: str = ""
    hotkeyNumber: int = 0

    def create(args):
        obj = CfgWorkspace()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Workspace ID"
        labels["display_name"] = "Display Name"
        labels["icon"] = "Preview Icon"
        labels["hotkeyNumber"] = "Activation Hotkey"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions