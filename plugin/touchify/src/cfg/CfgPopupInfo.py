from ..ext.extensions import Extensions


class CfgPopupInfo:
    text: str = ""
    action: str = ""
    icon: str = ""

    def create(args):
        obj = CfgPopupInfo()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        return self.text.replace("\n", "\\n")

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions