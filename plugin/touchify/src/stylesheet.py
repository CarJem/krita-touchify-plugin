"""
    Plugin for Krita UI Redesign, Copyright (C) 2020 Kapyia, Pedro Reis

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from krita import *

class Stylesheet:

    touchify_nt_toolbox = ""
    touchify_toggle_button = ""
    touchify_toolshelf_header = ""
    touchify_toolshelf_header_button = ""
    touchify_nt_toolbox_button = ""

    highlight_rgb = ""
    background_rgb = ""
    alternate_rgb = ""

    highlight_hex = ""
    background_hex = ""
    alternate_hex = ""
    inactive_text_color_hex = ""
    active_text_color_hex = ""


    def __init__(self) -> None:
        self.small_tab_size = 20
        self.no_borders_style = " QToolBar { border: none; } "
        self.small_tab_style = f"QTabBar::tab {{ height: {self.small_tab_size}px; }}"
        self.hide_menu_indicator = f"""QPushButton::menu-indicator {{ image: none; }} QToolButton::menu-indicator {{ image: none; }}"""
        self.rebuild_stylesheets()
        qApp.paletteChanged.connect(self.rebuild_stylesheets)

    def instance():
        try:
            return Stylesheet.__instance
        except AttributeError:
            Stylesheet.__instance = Stylesheet()
            return Stylesheet.__instance

    def rebuild_stylesheets(self): 





        self.background_raw = qApp.palette().color(QPalette.ColorRole.Window)
        self.highlight_raw = qApp.palette().color(QPalette.ColorRole.Highlight)
        self.alternate_raw = qApp.palette().color(QPalette.ColorRole.AlternateBase)

        self.background_rgb = f"{self.background_raw.red()},{self.background_raw.green()},{self.background_raw.blue()}"
        self.highlight_rgb = f"{self.highlight_raw.red()},{self.highlight_raw.green()},{self.highlight_raw.blue()}"
        self.alternate_rgb = f"{self.alternate_raw.red()},{self.alternate_raw.green()},{self.alternate_raw.blue()}"

        self.highlight_hex = self.highlight_raw.name().split("#")[1]
        self.background_hex = self.background_raw.name().split("#")[1]
        self.alternate_hex = self.alternate_raw.name().split("#")[1]
        self.inactive_text_color_hex = qApp.palette().color(QPalette.ColorRole.ToolTipText).name().split("#")[1]
        self.active_text_color_hex = qApp.palette().color(QPalette.ColorRole.WindowText).name().split("#")[1]

        self.touchify_nt_toolbox = f"""
                QFrame {{ 
                    background-color: #{self.background_hex};
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                }}
                
                QScrollArea {{ background: transparent; }}
                QScrollArea > QWidget > QWidget {{ background: transparent; }}
                QScrollArea > QWidget > QScrollBar {{ background: palette(base); }}
                
                QAbstractButton {{
                    background-color: #aa{self.background_hex};
                    border: none;
                    border-radius: 4px;
                }}
                
                QAbstractButton:checked {{
                    background-color: #cc{self.highlight_hex};
                }}
                
                QAbstractButton:hover {{
                    background-color: #{self.highlight_hex};
                }}
                
                QAbstractButton:pressed {{
                    background-color: #{self.alternate_hex};
                }}
            """
        
        self.touchify_nt_toolbox_button = f"""
                QPushButton::menu-indicator {{ 
                    image: none; 
                }} 
                
                QToolButton::menu-indicator {{ 
                    image: none; 
                }}
                
                QToolButton {{
                    padding: 4px;
                }}
        """

        self.touchify_toggle_button = f"""
                QToolButton, QPushButton {{
                    background-color: #aa{self.background_hex};
                    border: none;
                    border-radius: 4px;
                }}
                
                QToolButton:hover, QPushButton:hover {{
                    background-color: #{self.highlight_hex};
                }}
                
                QToolButton:pressed, QPushButton:pressed {{
                    background-color: #{self.alternate_hex};
                }}
                
                QToolButton::menu-indicator, QPushButton::menu-indicator {{ image: none; }}
                """

        self.touchify_toolshelf_header = f"""
                QPushButton {{
                    background-color: #{self.alternate_hex};
                    border: none;
                }}

                QPushButton:hover {{
                    background-color: #{self.highlight_hex};
                }}

                QPushButton:checked {{
                    background-color: #cc{self.highlight_hex};
                }}
                
                QPushButton:pressed {{
                    background-color: #{self.alternate_hex}; */
                }}

                QPushButton#back-widget {{
                    border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                    border: none;
                }}

                QPushButton#pin-widget {{
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                    border: none;
                }}

                QWidget#filler-widget {{
                    background-color: #{self.alternate_hex};
                    border: none;
                    border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                }}
                """

        self.touchify_toolshelf_header_button = f"""
                QToolButton {{
                    background-color: #aa{self.alternate_hex};
                    border: none;
                    border-radius: 4px;
                }}
                
                QToolButton:hover {{
                    background-color: #{self.highlight_hex};
                }}
                
                QToolButton:pressed {{
                    background-color: #{self.alternate_hex};
                }}

                QPushButton::menu-indicator {{ 
                    image: none; 
                }}

                QPushButton {{
                    background-color: #aa{self.alternate_hex};
                    border: none;
                    border-radius: 4px;
                }}
                
                QPushButton:hover {{
                    background-color: #{self.highlight_hex};
                }}
                
                QPushButton:pressed {{
                    background-color: #{self.alternate_hex};
                }}

                QPushButton::menu-indicator {{ 
                    image: none; 
                }}
                """

        self.propertygrid_selectordialog_listview = f"""
            QListWidget::item:selected {{ 
                background-color: #cc{self.highlight_hex}; 
            }}
        """

    def touchify_action_btn_popup(self, opacityLevel: float):



        return f"""
            QToolButton, QPushButton {{
                border-radius: 0px; 
                background-color: rgba({self.background_rgb},{opacityLevel});
                padding: 5px 5px;
                border: 0px solid transparent; 
                font-size: 12px
            }}
            
            QToolButton:hover, QPushButton:hover {{
                background-color: rgba({self.highlight_rgb},{opacityLevel});
            }}
                            
            QToolButton:pressed, QToolButton:pressed {{
                background-color: rgba({self.alternate_rgb},{opacityLevel});
            }}
        """

    def touchify_popup_frame(self, opacityAllowed: bool, opacityValue: float) -> str:
        if opacityAllowed:
            styleData = f"""opacity: {opacityValue};"""
        else:
            styleData = "opacity: 1"
        return f"""QFrame#popupFrame {styleData}"""

    def touchify_popup_titlebar(self, opacityAllowed: bool, opacityValue: float) -> str:
        if opacityAllowed:
            styleData = f"""opacity: {opacityValue};"""
        else:
            styleData = "opacity: 1"
        return f"""QWidget#popupFrameTitlebar {styleData}"""
    
