from ..ext.extensions import Extensions


class CfgToolboxPanelDocker:
    id: str = ""
    size_x: int = 0
    size_y: int = 0
    nesting_mode: str = "normal"
    panel_y: int = 0

    def create(args):
        obj = CfgToolboxPanelDocker()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Docker ID"
        labels["size_x"] = "Docker Width (leave unset for auto)"
        labels["size_y"] = "Docker Height (leave unset for auto)"
        labels["panel_y"] = "Panel Row"
        labels["nesting_mode"] = "Nesting Mode"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        restrictions["nesting_mode"] = {"type": "values", "entries": ["normal", "docking"]}
        restrictions["panel_x"] = {"type": "range", "min": 0, "max": 10}
        restrictions["panel_y"] = {"type": "range", "min": 0, "max": 10}
        return restrictions