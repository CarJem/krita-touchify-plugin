from ..ext.extensions import Extensions


class KB_Docker:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    isEnabled: bool = False

    def create(args):
        obj = KB_Docker()
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
        restrictions["id"] = {"type": "docker_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions