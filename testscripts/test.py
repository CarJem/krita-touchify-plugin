from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

print(Krita.instance().action('selection_tool_mode_replace').isVisible())
        


