from typing import Protocol
from dataclasses import dataclass



from PyQt5.QtWidgets import (QWidgetAction)

class WindowObj(Protocol):
    """Krita window received in createActions() of main extension file."""

    def createAction(
        self,
        name: str,
        description: str,
        menu: str, /
    ) -> QWidgetAction: ...

@dataclass
class WindowAPI:
    window: WindowObj

    def createAction(self, name: str, description: str, menu: str) -> QWidgetAction:
        self.window.createAction(name, description, menu)