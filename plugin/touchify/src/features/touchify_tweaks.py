# For autocomplete
from PyQt5 import QtWidgets, QtGui

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *


from ..ext.extensions import KritaExtensions

class TouchifyTweaks:

    def style_KisLayerView(self):
        docker = KritaExtensions.getDocker("KisLayerBox")
        if not docker:
            return

        wobj = docker.findChild(QWidget,'WdgLayerBox')

        last_toolbars = wobj.findChildren(QWidget, "touchify_layertoolbar")
        for ls_toolbar in last_toolbars:
            wobj.layout().removeWidget(ls_toolbar)
            ls_toolbar.deleteLater()

        last_toolbars_Q = wobj.findChildren(QObject, "touchify_layertoolbar")
        for ls_toolbar_Q in last_toolbars_Q:
            ls_toolbar_Q.deleteLater()

        toolbar = QToolBar(wobj)
        toolbar.setObjectName("touchify_layertoolbar")
        toolbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        toolbar.layout().setContentsMargins(0, 0, 0, 0)
        toolbar.layout().setSpacing(0)
        toolbar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        toolbar.setStyleSheet(f"""QToolBar {{ padding: 0; margin: 0; spacing: 0; }}""")
        wobj.layout().addWidget(toolbar)

        def create_button(action, icon=None):
            btn = QToolButton()
            btn.setDefaultAction(Krita.instance().action(action))
            if icon:
                btn.setIcon(Krita.instance().icon(icon))
            toolbar.addWidget(btn)

        def create_dropdown_button(actions, icon=None):
            btn = QToolButton()
            btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            btn.setStyleSheet(f"""QToolButton::menu-indicator {{image: none}}""")
            for action in actions:
                btn.addAction(Krita.instance().action(action))
            if icon:
                btn.setIcon(Krita.instance().icon(icon))
            toolbar.addWidget(btn)

        def create_spacer():
            empty = QWidget()
            empty.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
            toolbar.addWidget(empty)
 
        create_button("merge_layer")
        create_spacer()
        create_dropdown_button(["create_quick_group", "quick_ungroup"], "groupLayer")
        
    def style_CSS(self, window):
        full_style_sheet = f""""""
        window.setStyleSheet(full_style_sheet)

    def load(self, window):
        self.style_CSS(window)
        self.style_KisLayerView()

