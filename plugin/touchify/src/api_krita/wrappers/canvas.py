# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass

from krita import (
    Canvas as KritaCanvas
)

from touchify.src.api_krita.wrappers.view import ViewAPI


@dataclass
class CanvasAPI:
    """Wraps krita `Canvas` for typing, docs and PEP8 compatibility."""

    canvas: KritaCanvas

    def isValid(self):
        return self.canvas != None

    def __post_init__(self) -> None:
        def get_default_zoom_scale() -> float:
            default_value = 100
            if not self.isValid(): return default_value
            
            view = ViewAPI(self.canvas.view())
            if not view.isValid(): return default_value

            document = view.document
            if not document.isValid(): return default_value

            return document.dpi / 7200
        
        self._zoom_scale = get_default_zoom_scale()

    @property
    def rotation(self) -> float:
        """Settable property with rotation in degrees between `0` and `360`."""
        if self.isValid(): return self.canvas.rotation()
        else: return 0

    @rotation.setter
    def rotation(self, angle_deg: float) -> None:
        """Set canvas rotation with float representing angle in degrees."""
        if self.isValid(): self.canvas.setRotation(angle_deg % 360)

    @property
    def zoom(self) -> float:
        """
        Settable property with zoom level expressed in %.

        Add a workaround for zoom detected by krita affected by document dpi.
        """
        if self.isValid(): return self.canvas.zoomLevel() / self._zoom_scale
        else: return 1

    @zoom.setter
    def zoom(self, zoom: float) -> None:
        """Set zoom of canvas by providing zoom level expressed in %."""
        if self.isValid(): self.canvas.setZoomLevel(zoom*0.01)
