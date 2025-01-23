from krita import *
from bulicommander.bulicommander import BuliCommander




qwin = Krita.instance().activeWindow().qwindow()
file_manager = BuliCommander(qwin)
file_manager.start()
window: QWidget = file_manager._BuliCommander__uiController._BCUIController__window
welcome_page = qwin.findChild(QWidget,'KisWelcomePage')
stack_widget = welcome_page.findChild(QStackedWidget,'recentDocsStackedWidget')
index = stack_widget.addWidget(window)
stack_widget.setCurrentIndex(index)

        