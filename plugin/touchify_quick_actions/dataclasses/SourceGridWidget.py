from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from jemlib.api_touchify.config.quick_actions.QuickActionsPage import QuickActionsGrid
    from jemlib.api_touchify.config.quick_actions.QuickActionsItem import QuickActionsItem

class SourceGridWidget(TypedDict):
    preset: "QuickActionsItem"
    grid: "QuickActionsGrid"
    index: int
    name: str