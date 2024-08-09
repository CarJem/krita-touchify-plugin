from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


#Krita.instance().notifier().configurationChanged.emit()
#Krita.instance().activeWindow().qwindow().slotPreferences()
                                

Krita.instance().activeWindow().qwindow().setStyleSheet(f"""    
    TouchifyActionPushButton | TouchifyActionToolButton:hover {{
                  
    }}
""")