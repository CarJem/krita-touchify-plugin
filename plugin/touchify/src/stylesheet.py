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
    def __init__(self) -> None:
        self.small_tab_size = 20

        self.no_borders_style = " QToolBar { border: none; } "

        self.small_tab_style = f"QTabBar::tab {{ height: {self.small_tab_size}px; }}"

        self.hide_menu_indicator = f"""QPushButton::menu-indicator {{ image: none; }} QToolButton::menu-indicator {{ image: none; }}"""

        self.touchify_toggle_button = f"""
                QToolButton, QPushButton {{
                    background-color: palette(window);
                    border: none;
                    border-radius: 4px;
                }}
                
                QToolButton:hover, QPushButton:hover {{
                    background-color: palette(highlight);
                }}
                
                QToolButton:pressed, QPushButton:pressed {{
                    background-color: palette(alternate-base);
                }}
                
                QToolButton::menu-indicator, QPushButton::menu-indicator {{ image: none; }}
                """

        self.touchify_toolshelf_header = f"""

                QWidget#toolshelf-header {{
                    background-color: palette(alternate-base);
                    border: none;
                }}

                QWidget#toolshelf-tablist-row {{
                    background-color: palette(alternate-base);
                    border: none;
                }}

                QPushButton, QToolButton {{
                    background-color: palette(alternate-base);
                    border: none;
                }}

                QPushButton:hover, QToolButton:hover {{
                    background-color: palette(highlight);
                }}

                QPushButton:checked, QToolButton:checked {{
                    background-color: palette(highlight);
                }}
                
                QPushButton:pressed, QToolButton:pressed {{
                    background-color: palette(alternate-base);
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

                QPushButton::menu-indicator, QToolButton::menu-indicator {{ 
                    image: none; 
                }}

                QPushButton#menu-widget {{
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                    border: none;
                }}

                QWidget#filler-widget {{
                    background-color: palette(alternate-base);
                    border: none;
                    border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                }}
                """

        self.propertygrid_selectordialog_listview = f"""
            QListWidget::item:selected {{ 
                background-color: palette(alternate-base);
            }}
        """

    def instance():
        try:
            return Stylesheet.__instance
        except AttributeError:
            Stylesheet.__instance = Stylesheet()
            return Stylesheet.__instance

    def touchify_action_btn_popup(self, opacityLevel: float):

        return f"""
            QToolButton, QPushButton {{
                border-radius: 0px; 
                background-color: palette(window);
                padding: 5px 5px;
                border: 0px solid transparent; 
                font-size: 12px;
                opacity: {opacityLevel};
            }}
            
            QToolButton:hover, QPushButton:hover {{
                background-color: palette(highlight);
                opacity: {opacityLevel};
            }}
                            
            QToolButton:pressed, QToolButton:pressed {{
                background-color: palette(alternate-base);
                opacity: {opacityLevel};
            }}
        """

    def touchify_popup_frame(self, opacityAllowed: bool, opacityValue: float) -> str:
        if opacityAllowed:
            styleData = f"""opacity: {opacityValue};"""
        else:
            styleData = "opacity: 1;"
        return f"""QFrame#popupFrame {styleData}"""

    def touchify_popup_titlebar(self, opacityAllowed: bool, opacityValue: float) -> str:
        if opacityAllowed:
            styleData = f"""opacity: {opacityValue};"""
        else:
            styleData = "opacity: 1;"
        return f"""QWidget#popupFrameTitlebar {styleData}"""
    
