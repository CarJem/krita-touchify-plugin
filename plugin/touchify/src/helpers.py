from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .extension import TouchifyExtension

class TouchifyHelpers:

    def getExtension() -> "TouchifyExtension":
        extensions = Krita.instance().extensions()
        for ext in extensions:
            if hasattr(ext, "DEV_HOOK_FIND_PLUGIN"):
                if getattr(ext, "DEV_HOOK_FIND_PLUGIN") == "TOUCHIFY":
                    return ext
        return None