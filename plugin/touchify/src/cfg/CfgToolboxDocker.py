from ..ext.extensions import Extensions


class CfgToolboxDocker:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    isEnabled: bool = False
    nesting_mode: str = "normal"

    def create(args):
        obj = CfgToolboxDocker()
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
        labels["id"] = "Docker ID"
        labels["icon"] = "Display Icon"
        labels["size_x"] = "Docker Width (leave unset for auto)"
        labels["size_x"] = "Docker Height (leave unset for auto)"
        labels["isEnabled"] = "Active"
        labels["nesting_mode"] = "Nesting Mode"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["nesting_mode"] = {"type": "values", "entries": ["normal", "docking"]}
        return restrictions