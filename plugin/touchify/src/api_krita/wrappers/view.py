# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from functools import cached_property




from krita import (
    Krita as Api,
    View as KritaView,
    Resource as KritaResource
)

from touchify.src.api_krita.enums import BlendingMode


from touchify.src.api_krita.wrappers.document import DocumentAPI
from touchify.src.api_krita.wrappers.color import ManagedColorAPI

@dataclass
class ViewAPI:
    """Wraps krita `View` for typing, documentation and PEP8 compatibility."""

    view: KritaView

    def isValid(self):
        return self.view != None
    
    def document(self) -> DocumentAPI:
        if self.isValid(): return DocumentAPI(self.view.document())
        else: return DocumentAPI(None)

    @property
    def foregroundColor(self) -> ManagedColorAPI:
        if self.isValid(): return ManagedColorAPI(self.view.foregroundColor())
        else: return ManagedColorAPI(None)

    @foregroundColor.setter
    def foregroundColor(self, color_data: ManagedColorAPI):
        if self.isValid(): self.view.setForeGroundColor( color_data.color )

    @property
    def foregroundColor(self) -> ManagedColorAPI:
        if self.isValid(): return ManagedColorAPI(self.view.foregroundColor())
        else: return ManagedColorAPI(None)

    @foregroundColor.setter
    def foregroundColor(self, color_data: ManagedColorAPI):
        if self.isValid() and color_data.isValid(): self.view.setBackGroundColor( color_data.color )

    @cached_property
    def preset_map(self) -> dict[str, KritaResource]:
        """Return dictionary mapping preset names to krita preset objects."""
        return Api.instance().resources('preset')

    @property
    def brush_preset(self) -> str:
        """Settable property with active brush preset name."""
        if self.isValid(): return self.view.currentBrushPreset().name()
        else: return ""

    @brush_preset.setter
    def brush_preset(self, preset_name: str) -> None:
        if not self.isValid(): return
        """Set brush preset inside this `View` using its name."""
        if preset_name in self.preset_map:
            self.view.setCurrentBrushPreset(self.preset_map[preset_name])

    @property
    def blending_mode(self) -> BlendingMode:
        """Settable property with active blending mode enum."""
        if self.isValid(): return BlendingMode(self.view.currentBlendingMode())
        else: return BlendingMode.NORMAL

    @blending_mode.setter
    def blending_mode(self, mode: BlendingMode) -> None:
        """Set blending mode inside this `View` using its enum."""
        if self.isValid(): self.view.setCurrentBlendingMode(mode.value)

    @property
    def opacity(self) -> int:
        """Settable property with painting opacity as %."""
        if self.isValid(): return round(100*self.view.paintingOpacity())
        else: return 100

    @opacity.setter
    def opacity(self, opacity: int) -> None:
        """Set painting opacity inside this `View`."""
        if self.isValid(): self.view.setPaintingOpacity(0.01*round(opacity))

    @property
    def flow(self) -> int:
        """Settable property with painting flow as %."""
        if self.isValid(): return round(100*self.view.paintingFlow())
        else: return 100

    @flow.setter
    def flow(self, flow: int) -> None:
        """Set painting flow inside this `View`."""
        if self.isValid(): self.view.setPaintingFlow(0.01*round(flow))

    @property
    def brush_size(self) -> float:
        """Settable property with brush size in pixels."""
        if self.isValid(): return self.view.brushSize()
        else: return 16

    @brush_size.setter
    def brush_size(self, brush_size: float) -> None:
        """Set brush size inside this `View`."""
        if self.isValid(): self.view.setBrushSize(brush_size)

    @property
    def brush_rotation(self) -> float:
        """Settable property with brush rotation in deg between 0 and 360."""
        if self.isValid(): return self.view.brushRotation()
        else: return 0

    @brush_rotation.setter
    def brush_rotation(self, rotation: float) -> None:
        """Set brush rotation with float representing angle in degrees."""
        if self.isValid(): self.view.setBrushRotation(rotation % 360)
