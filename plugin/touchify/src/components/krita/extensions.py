
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *


class KritaExtensions:

    def showQuickMessage(message: str):
        Krita.instance().activeWindow().activeView().showFloatingMessage(message, Krita.instance().icon('move_layer_up'), 1000, 0)

    def formatActionText(text: str):
        seperator = " "
        segments = text.split(seperator)
        edited_segments = []

        for seg in segments:
            if seg.startswith("&") and len(seg) != 1:
                edited_segments.append(seg[1:])
            else:
                edited_segments.append(seg)
            

        return seperator.join(edited_segments)
