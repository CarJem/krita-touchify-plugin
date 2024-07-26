from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



recent_files_action = Krita.instance().action("file_open_recent")
for item in recent_files_action.menu().actions():
    print(item.objectName())
