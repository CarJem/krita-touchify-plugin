from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *

qwin = Krita.instance().activeWindow().qwindow()
wobj = qwin.centralWidget()

stylesheet = f"""\n 
            QTabBar {{ icon-size: 12px 12px; }}
            QTabBar::tab {{ height: {20}px;  }} 
            QTabBar::close-button {{ margin: 2px 2px 2px 2px; }} 
            \n"""

wobj.setStyleSheet(stylesheet)