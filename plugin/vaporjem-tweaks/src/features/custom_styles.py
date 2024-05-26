# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .src.ext.PyKrita import *
else:
    from krita import *

class CustomStyles:

    def applyStyles(window):
        full_style_sheet = f"""
        """

        window.setStyleSheet(full_style_sheet)