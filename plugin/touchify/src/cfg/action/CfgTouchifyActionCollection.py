
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction

class CfgTouchifyActionCollection:
    
    row_name: str = "Actions Row"

    def __init__(self, **args) -> None:
        from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
        self.actions: TypedList[CfgTouchifyAction] = []
        Extensions.dictToObject(self, args)
        self.actions = Extensions.init_list(args, "actions", CfgTouchifyAction)

    def forceLoad(self):
        from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
        self.actions = TypedList(self.actions, CfgTouchifyAction)

    def __str__(self):
        return self.row_name
    
    def propertygrid_hints(self):
        hints = {}
        return hints
    
    def propertygrid_hidden(self):
        result = []
        return result
    
    def propertygrid_sorted(self):
        return [
            "row_name",
            "actions",
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["actions"] = "Actions"
        labels["row_name"] = "Row Name"
        return labels
    
    
    def propertygrid_ismodel(self):
        return True

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions