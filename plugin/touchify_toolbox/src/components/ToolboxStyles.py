
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from jemlib.api_krita import KritaAPI
from touchify.src.components.widgets.triggers.TriggerButton import TriggerButton
from touchify_toolbox.src.config.ToolboxData import ToolboxData


class ToolboxStyles:
    class ButtonStyle(QProxyStyle):
        def __init__(self, key: str, delay: int):
            super().__init__(key)
            self.menuDelay = delay

        def styleHint(self, element, option,
                    widget, returnData):

            if element == QStyle.SH_ToolButton_PopupDelay:
                return self.menuDelay

            return super().styleHint(element, option, widget, returnData);

    class ButtonFilter(QObject):
        def eventFilter(self, a0, a1):
            if a0 == self and a1.type() == QEvent.Type.Enter:
                if len(KritaAPI.get_documents()) == 0: # disable buttons before document is visible
                    self.setEnabled(False)
                else:
                    self.setEnabled(True)
            return super().eventFilter(a0, a1)

    class ThemeData:
        def __init__(self, cfg: ToolboxData, orientation: Qt.Orientation):
            self.highlight = qApp.palette().color(QPalette.ColorRole.Highlight)
            self.highlight_hex = self.highlight.name().split("#")[1]

            self.dark = qApp.palette().color(QPalette.ColorRole.Dark)
            self.dark_hex = self.dark.name().split("#")[1]

            self.light = qApp.palette().color(QPalette.ColorRole.Light)
            self.light_hex = self.light.name().split("#")[1]

            self.dark = qApp.palette().color(QPalette.ColorRole.Dark)
            self.dark_hex = self.dark.name().split("#")[1]

            self.mid = qApp.palette().color(QPalette.ColorRole.Mid)
            self.mid_hex = self.dark.name().split("#")[1]

            self.button = qApp.palette().color(QPalette.ColorRole.Button)
            self.button_hex = self.dark.name().split("#")[1]

            self.background = qApp.palette().color(QPalette.ColorRole.Background)
            self.background_hex = self.background.name().split("#")[1]

            self.base = qApp.palette().color(QPalette.ColorRole.Base)
            self.base_hex = self.base.name().split("#")[1]

            self.alternate_base = qApp.palette().color(QPalette.ColorRole.AlternateBase)
            self.alternate_base_hex = self.alternate_base.name().split("#")[1]

            self.window = qApp.palette().color(QPalette.ColorRole.Window)
            self.window_hex = self.window.name().split("#")[1]

            self.tooltip_text = qApp.palette().color(QPalette.ColorRole.ToolTipText)
            self.tooltip_text_hex = self.tooltip_text.name().split("#")[1]

            self.window_text = qApp.palette().color(QPalette.ColorRole.WindowText)
            self.window_text_hex = self.window_text.name().split("#")[1]

            self.theme = cfg.theme
            self.submenu_delay = cfg.submenu_delay
            self.orienation = orientation


    class Themes:
        @staticmethod
        def Button(data: "ToolboxStyles.ThemeData"):
            if data.theme == ToolboxData.ThemeStyle.Krita:
                return f"""
                    TriggerButton {{
                        background-color: transparent;
                        border: 1px solid transparent;
                        border-radius: 2px;
                        padding: 4px;
                    }}
                    
                    TriggerButton[toggled="true"] {{
                        background-color: #{data.highlight_hex};
                        border: 1px solid #{data.button_hex};
                    }}

                    TriggerButton[menu_toggled="true"] {{
                        border: 1px solid #{data.highlight_hex};
                    }}

                    TriggerButton[toggled="true"]:hover {{
                        background-color: #{data.highlight_hex};
                        border: 1px solid #{data.button_hex};
                    }}

                    TriggerButton[toggled="true"]:pressed {{
                        background-color: #{data.dark_hex};
                        border: 1px solid #{data.button_hex};
                    }}
                    
                    TriggerButton:hover {{
                        background-color: #{data.light_hex};
                        border: 1px solid #{data.button_hex};
                    }}
                    
                    TriggerButton:pressed {{
                        background-color: #{data.dark_hex};
                        border: 1px solid #{data.button_hex};
                    }}

                    TriggerButton::menu-indicator {{ 
                        image: none; 
                    }}
                """
            else:
                return f"""
                    TriggerButton {{
                        background-color: #{data.base_hex};
                        border: 1px solid #{data.base_hex};
                        border-radius: 4px;
                        padding: 4px;
                    }}
                    
                    TriggerButton[toggled="true"] {{
                        background-color: #{data.highlight_hex};
                    }}

                    TriggerButton[menu_toggled="true"] {{
                        border: 1px solid #{data.highlight_hex};
                    }}
                    
                    TriggerButton:hover {{
                        background-color: #{data.highlight_hex};
                    }}
                    
                    TriggerButton:pressed {{
                        background-color: #{data.alternate_base_hex};
                    }}

                    TriggerButton::menu-indicator {{ 
                        image: none; 
                    }}
                """
        
        @staticmethod
        def Common(data: "ToolboxStyles.ThemeData"):
            if data.theme == ToolboxData.ThemeStyle.Krita:
                return f"""
                    QScrollArea {{ background: transparent; }}
                    QScrollArea > QWidget > QScrollBar {{ background: palette(base); }}
                """
            else:
                return f"""
                    QScrollArea {{ background: transparent; }}
                    QScrollArea > QWidget > QWidget {{ background: transparent; }}
                    QScrollArea > QWidget > QScrollBar {{ background: palette(base); }}
                """
        
        @staticmethod
        def Frames(data: "ToolboxStyles.ThemeData"):
            def Horizontal():
                if data.theme == ToolboxData.ThemeStyle.Krita:
                    return f"""
                        Section {{ 
                            background-color: transparent
                            border-radius: 0px;
                            padding: 0px;
                        }}
                    """
                else:
                    return f"""
                        Section {{ 
                            background-color: #{data.base_hex};
                            border-radius: 4px;
                            padding: 0px;
                        }}
                    """
            
            def Vertical():
                if data.theme == ToolboxData.ThemeStyle.Krita:
                    return f"""
                        Section {{ 
                            background-color: transparent
                            border-radius: 0px;
                            padding: 0px;
                        }}
                    """
                else:
                    return f"""
                        Section {{ 
                            background-color: #{data.base_hex};
                            border-radius: 4px;
                            padding: 0px;
                        }}
                    """

            if data.orienation == Qt.Orientation.Horizontal: return Horizontal()
            else: return Vertical()

        @staticmethod
        def ButtonPalette(btn: TriggerButton, data: "ToolboxStyles.ThemeData"):
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Button, data.highlight)
            btn.setPalette(palette)


    @staticmethod
    def getStyleSheet(style_data: "ToolboxStyles.ThemeData"):
        return f"""
        {ToolboxStyles.Themes.Common(style_data)}
        {ToolboxStyles.Themes.Button(style_data)}
        {ToolboxStyles.Themes.Frames(style_data)}
        """
    
    @staticmethod
    def setButtonStyleSheet(btn: TriggerButton, style_data: "ToolboxStyles.ThemeData"):
        btn.setStyle(ToolboxStyles.ButtonStyle("fusion", style_data.submenu_delay))
        ToolboxStyles.Themes.ButtonPalette(btn, style_data)
        btn.installEventFilter(ToolboxStyles.ButtonFilter())