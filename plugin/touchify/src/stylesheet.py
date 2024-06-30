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

highlight = qApp.palette().color(QPalette.Highlight).name().split("#")[1]
background = qApp.palette().color(QPalette.Window).name().split("#")[1]
alternate = qApp.palette().color(QPalette.AlternateBase).name().split("#")[1]
inactive_text_color = qApp.palette().color(QPalette.ToolTipText).name().split("#")[1]
active_text_color = qApp.palette().color(QPalette.WindowText).name().split("#")[1]

small_tab_size = 20

no_borders_style = " QToolBar { border: none; } "

nu_toolbox_style = f"""
            QWidget {{ 
                background-color: #01{alternate};
            }}
            
            .QScrollArea {{ 
                background-color: #00{background};
            }}
            
            QScrollArea * {{ 
                background-color: #00000000;
            }}
            
            QScrollArea QToolTip {{
                background-color: #{active_text_color};                         
            }}
            
            QAbstractButton {{
                background-color: #aa{background};
                border: none;
                border-radius: 4px;
            }}
            
            QAbstractButton:checked {{
                background-color: #cc{highlight};
            }}
            
            QAbstractButton:hover {{
                background-color: #{highlight};
            }}
            
            QAbstractButton:pressed {{
                background-color: #{alternate};
            }}
        """

nu_toggle_button_style = f"""
        QToolButton {{
            background-color: #aa{background};
            border: none;
            border-radius: 4px;
        }}
        
        QToolButton:hover {{
            background-color: #{highlight};
        }}
        
        QToolButton:pressed {{
            background-color: #{alternate};
        }}


        QPushButton {{
            background-color: #aa{background};
            border: none;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: #{highlight};
        }}
        
        QPushButton:pressed {{
            background-color: #{alternate};
        }}
        """

nu_toolshelf_header_style = f"""
        QPushButton {{
            background-color: #aa{background};
            border: none;
        }}

        QPushButton:hover {{
            background-color: #{highlight};
        }}

        QPushButton:checked {{
            background-color: #cc{highlight};
        }}
        
        QPushButton:pressed {{
            background-color: #{alternate};
        }}

        QPushButton#back-widget {{
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
        }}

        QPushButton#pin-widget {{
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}

        QWidget#filler-widget {{
            background-color: #aa{background};
            border: none;
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
        }}
        """

nu_toolshelf_button_style = f"""
        QToolButton {{
            background-color: #aa{background};
            border: none;
            border-radius: 4px;
        }}
        
        QToolButton:hover {{
            background-color: #{highlight};
        }}
        
        QToolButton:pressed {{
            background-color: #{alternate};
        }}
        """

small_tab_style = f"QTabBar::tab {{ height: {small_tab_size}px; }}"

def touchify_popup_frame(opacityAllowed: bool, opacityValue: float) -> str:
    if opacityAllowed:
        styleData = f"""opacity: {opacityValue};"""
    else:
        styleData = "opacity: 1"
    return f"""QFrame#popupFrame {styleData}"""

def touchify_popup_titlebar(opacityAllowed: bool, opacityValue: float) -> str:
    if opacityAllowed:
        styleData = f"""opacity: {opacityValue};"""
    else:
        styleData = "opacity: 1"
    return f"""QWidget#popupFrameTitlebar {styleData}"""