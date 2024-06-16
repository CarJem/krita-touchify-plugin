from ..ext.extensions import Extensions


class KB_Actions:
    id: str = ""
    icon: str = ""
    isEnabled: bool = False

    def create(args):
        obj = KB_Actions()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        if not self.isEnabled:
            name = "(Disabled) " + name
        return name

    def forceLoad(self):
        pass

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions