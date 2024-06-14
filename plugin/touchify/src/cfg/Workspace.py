from ..ext.extensions import Extensions


class Workspace:
    display_name: str = ""
    id: str = ""
    icon: str = ""
    hotkeyNumber: int = 0

    def create(args):
        obj = Workspace()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_groups(self):
        groups = {}
        groups["general"] = {"name": "General Settings", "items": ["id", "icon", "hotkeyNumber"]}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions