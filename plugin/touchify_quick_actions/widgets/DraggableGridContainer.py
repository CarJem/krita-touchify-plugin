"""Grid container and click surface for brush presets.

`ClickableGridWidget` represents the area that holds brush buttons for one
grid and handles drag & drop between grids. `DraggableGridContainer` wraps
the grid header (collapse + name row) and the `ClickableGridWidget`, and also
accepts drops on the header so brushes can be moved by dropping on the grid
name.
"""

from typing import TYPE_CHECKING
from PyQt5.QtWidgets import QWidget




if TYPE_CHECKING:
    from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker
    from touchify_quick_actions.dataclasses.GridConfig import GridInfo
    from touchify_quick_actions.dataclasses.GridPresetItem import GridPresetItem

from ..dataclasses.SourceGridWidget import SourceGridWidget

class DraggableGridContainer(QWidget):
    """Container for draggable grids"""

    def __init__(self, grid_info: "GridInfo", parent_docker: "QuickActionsDocker"):
        super().__init__()
        self.grid_info = grid_info
        self.parent_docker = parent_docker
        # Allow drops on the header/container itself (grid name row area)
        # so users can drop brushes directly onto a grid header.
        self.setAcceptDrops(True)

    # --- Drag & Drop on header / container ---------------------------------

    def dragEnterEvent(self, event):
        """Accept brush drags when hovering over the grid header/container."""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith("brush_preset:") or text.startswith("brush_presets_multi:"):
                event.acceptProposedAction()

    def dropEvent(self, event):
        """
        Handle drops on the grid header/container.

        Requirement: when one or more DraggableBrushButtons are dropped while
        hovering a gridname row, place them inside this grid and unhide it.
        """
        if not event.mimeData().hasText():
            return

        text = event.mimeData().text()

        # Ensure grid is un-collapsed / visible
        if self.grid_info.is_collapsed:
            # Use existing toggle logic in the docker to update icon + visibility
            try:
                self.parent_docker.toggle_grid_collapse(self.grid_info)
            except Exception:
                # Fallback: force it visible if toggle is not available
                self.grid_info.is_collapsed = False
                self.parent_docker.update_grid_visibility(self.grid_info)

        if text.startswith("brush_preset:"):
            self._handle_header_brush_drop(event, text)
        elif text.startswith("brush_presets_multi:"):
            self._handle_header_multi_brush_drop(event, text)

    # --- Helper methods for header drops -----------------------------------

    def _find_source_preset(self, preset_name: str):
        """Find source preset in all grids (same logic as ClickableGridWidget)."""
        for grid in self.parent_docker.grids:
            for i, preset in enumerate(grid.brush_presets):
                if preset.name() == preset_name:
                    return preset, grid, i
        return None, None, -1

    def _handle_header_brush_drop(self, event, text: str):
        """Single preset dropped on grid header: append to this grid."""
        preset_name = text.split(":", 1)[1]

        source_preset, source_grid, source_index = self._find_source_preset(preset_name)

        if not (source_preset and source_grid):
            return

        # Remove from old position
        source_grid.brush_presets.pop(source_index)

        target_grid = self.grid_info
        target_index = len(target_grid.brush_presets)

        # Insert into target grid at the end
        target_grid.brush_presets.insert(target_index, source_preset)

        # Update affected grids
        if source_grid is target_grid:
            self.parent_docker.update_grid(target_grid)
        else:
            self.parent_docker.update_grid(source_grid)
            self.parent_docker.update_grid(target_grid)

        self.parent_docker.save_grids_data()
        event.acceptProposedAction()

    def _handle_header_multi_brush_drop(self, event, text):
        """Multiple presets dropped on grid header: append all to this grid."""
        # Parse preset names from mime data
        preset_names_str = text.split(":", 1)[1]
        preset_names = [name.strip() for name in preset_names_str.split(",") if name.strip()]

        # Find all source presets and their positions
        source_presets_data: list[SourceGridWidget] = []
        for preset_name in preset_names:
            source_preset, source_grid, source_index = self._find_source_preset(preset_name)
            if source_preset and source_grid is not None:
                source_presets_data.append(
                    {"preset": source_preset, "grid": source_grid, "index": source_index}
                )

        if not source_presets_data:
            return

        # Group by grid first to safely remove from source positions
        grids_to_update: dict[str, SourceGridWidget] = {}
        for data in source_presets_data:
            grid = data["grid"]
            grid_name = grid.get("name", id(grid))
            if grid_name not in grids_to_update:
                grids_to_update[grid_name] = {"grid_info": grid, "presets_data": []}
            grids_to_update[grid_name]["presets_data"].append(data)

        # Remove presets from their original grids (reverse index order per grid)
        for grid_data in grids_to_update.values():
            grid_info = grid_data["grid_info"]
            presets_data = grid_data["presets_data"]
            for data in sorted(presets_data, key=lambda x: x["index"], reverse=True):
                grid_info.brush_presets.pop(data["index"])

        # Append all presets to this grid in the order they were dragged
        target_grid = self.grid_info
        for data in source_presets_data:
            target_grid.brush_presets.append(data["preset"])

        # Update affected grids
        for grid_data in grids_to_update.values():
            grid_info = grid_data["grid_info"]
            self.parent_docker.update_grid(grid_info)
        if target_grid not in [g["grid_info"] for g in grids_to_update.values()]:
            self.parent_docker.update_grid(target_grid)

        # Clear selection and save
        self.parent_docker.clear_selection()
        self.parent_docker.save_grids_data()
        event.acceptProposedAction()
