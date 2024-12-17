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
        
    def touchify_edit_mode_selector(self):
        base_color = qApp.palette().highlight().color()
        base_factor = 25

        normal_color = f"rgba({base_color.red()},{base_color.green()},{base_color.blue()},{0})"
        hover_color = f"rgba({base_color.red() + base_factor},{base_color.green() + base_factor},{base_color.blue() + base_factor},{150})"
        press_color = f"rgba({base_color.red() - base_factor},{base_color.green() - base_factor},{base_color.blue() - base_factor},{150})"

        normal_style = f"QPushButton {{ background-color: {normal_color}; border: none; }}"
        hover_style = f"QPushButton:hover {{ background-color: {hover_color}; border: none; }}"
        pressed_style = f"QPushButton:pressed {{ background-color: {press_color}; border: none; }}"
        
        stylesheet = f"{normal_style} {hover_style} {pressed_style}"
        return stylesheet

    def touchify_action_btn_popup(self):

        return f"""
            QToolButton, QPushButton {{
                border-radius: 0px; 
                background-color: palette(window);
                padding: 5px 5px;
                border: 0px solid transparent; 
                font-size: 12px;
            }}
            
            QToolButton:hover, QPushButton:hover {{
                background-color: palette(highlight);
            }}
                            
            QToolButton:pressed, QToolButton:pressed {{
                background-color: palette(alternate-base);
            }}
        """
    
