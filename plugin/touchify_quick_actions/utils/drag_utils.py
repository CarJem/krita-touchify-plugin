"""Helpers for drag/drop payloads used by brush buttons and grids.

We currently use simple, name-based payloads to stay compatible with existing
behavior:
  - Single brush:  "brush_preset:<name>"
  - Multi brush:   "brush_presets_multi:<name1,name2,...>"
  - Single grid:   "grid:<name>"
  - Multi grid:    "grids_multi:<name1,name2,...>"

If we ever need richer payloads again (e.g., per-instance IDs), we can extend
these helpers in one place without touching widget code.
"""

def encode_single(preset_name: str) -> str:
    """Encode a single preset name into the drag text payload."""
    return f"brush_preset:{preset_name}"


def encode_multi(preset_names) -> str:
    """Encode multiple preset names (in order) into the drag text payload."""
    names = [name for name in preset_names if name]
    return "brush_presets_multi:" + ",".join(names)


def decode_single(text: str):
    """Decode a single preset payload, returning the preset name or None."""
    if not text.startswith("brush_preset:"):
        return None
    return text.split(":", 1)[1]


def decode_multi(text: str):
    """Decode a multi-preset payload, returning a list of preset names."""
    if not text.startswith("brush_presets_multi:"):
        return []
    payload = text.split(":", 1)[1]
    return [name.strip() for name in payload.split(",") if name.strip()]


def encode_grid_single(grid_name: str) -> str:
    """Encode a single grid name into the drag text payload."""
    return f"grid_drag:{grid_name}"


def encode_grid_multi(grid_names) -> str:
    """Encode multiple grid names (in order) into the drag text payload."""
    names = [name for name in grid_names if name]
    return "grids_drag_multi:" + ",".join(names)


def decode_grid_single(text: str):
    """Decode a single grid payload, returning the grid name or None."""
    if not text.startswith("grid_drag:"):
        return None
    return text.split(":", 1)[1]


def decode_grid_multi(text: str):
    """Decode a multi-grid payload, returning a list of grid names."""
    if not text.startswith("grids_drag_multi:"):
        return []
    payload = text.split(":", 1)[1]
    return [name.strip() for name in payload.split(",") if name.strip()]


def is_grid_drag(text: str) -> bool:
    """Check if the drag payload is a grid drag operation."""
    return text.startswith("grid_drag:") or text.startswith("grids_drag_multi:")