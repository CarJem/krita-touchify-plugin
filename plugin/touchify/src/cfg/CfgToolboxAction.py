from ..ext.extensions import Extensions


class CfgToolboxAction:
    id: str = ""
    icon: str = ""
    isEnabled: bool = False

    def create(args):
        obj = CfgToolboxAction()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        if not self.isEnabled:
            name = "(Disabled) " + name
        return name

    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["isEnabled"] = "Active"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["id"] = {"type": "action_selection"}
        return restrictions