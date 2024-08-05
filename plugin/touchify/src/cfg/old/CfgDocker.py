from ...ext.extensions_json import JsonExtensions as Extensions


class CfgDocker:
    display_name: str = ""
    docker_name: str = ""
    icon: str = ""

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def forceLoad(self):
        pass

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def propertygrid_groups(self):
        groups = {}
        return groups
    
    def propertygrid_labels(self):
        labels = {}
        labels["docker_name"] = "Docker ID"
        labels["display_name"] = "Text"
        labels["icon"] = "Icon"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["docker_name"] = {"type": "docker_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions