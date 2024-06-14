from ..ext.extensions import Extensions


class Docker:
    display_name: str = ""
    docker_name: str = ""
    icon: str = ""
    hotkeyNumber: int = 0

    def create(args):
        obj = Docker()
        Extensions.dictToObject(obj, args)
        return obj

    def forceLoad(self):
        pass

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def propertygrid_groups(self):
        groups = {}
        groups["general"] = {"name": "General Settings", "items": ["icon", "hotkeyNumber"]}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["docker_name"] = {"type": "docker_selection"}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions