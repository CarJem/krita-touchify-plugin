from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker
    from touchify_quick_actions.dataclasses.GridConfig import GridInfo, GridPresetItem

class SourceGridWidget(TypedDict):
    preset: "GridPresetItem"
    grid: "GridInfo"
    index: int
    name: str