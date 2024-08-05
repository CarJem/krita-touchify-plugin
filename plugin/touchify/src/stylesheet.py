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

highlight = qApp.palette().color(QPalette.ColorRole.Highlight).name().split("#")[1]
background = qApp.palette().color(QPalette.ColorRole.Window).name().split("#")[1]
alternate = qApp.palette().color(QPalette.ColorRole.AlternateBase).name().split("#")[1]
inactive_text_color = qApp.palette().color(QPalette.ColorRole.ToolTipText).name().split("#")[1]
active_text_color = qApp.palette().color(QPalette.ColorRole.WindowText).name().split("#")[1]

small_tab_size = 20
no_borders_style = " QToolBar { border: none; } "
small_tab_style = f"QTabBar::tab {{ height: {small_tab_size}px; }}"
hide_menu_indicator = f"""QPushButton::menu-indicator {{ image: none; }}"""

propertygrid_selectordialog_listview = f"""
    QListWidget::item:selected {{ 
        background-color: #cc{highlight}; 
    }}
"""

touchify_nt_toolbox = f"""
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

touchify_toggle_button = f"""
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

touchify_toolshelf_header = f"""
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
            border: none;
        }}

        QPushButton#pin-widget {{
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            border: none;
        }}

        QWidget#filler-widget {{
            background-color: #aa{background};
            border: none;
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
        }}
        """

touchify_toolshelf_header_button = f"""
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

        QPushButton::menu-indicator {{ 
            image: none; 
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

        QPushButton::menu-indicator {{ 
            image: none; 
        }}
        """


def touchify_action_btn_toolshelf(isFlat: bool):
        flatStyle = f"""
            QToolButton  {{
                border: 0px solid transparent;
            }}
        """
        
        result = f"""QToolButton::menu-indicator {{ image: none; }}"""
        
        if isFlat:
            result += flatStyle
            
        return result
            

def touchify_action_btn_popup(opacityLevel: float):
    return f"""
        QToolButton {{
            border-radius: 0px; 
            background-color: rgba(0,0,0,{opacityLevel}); 
            padding: 5px 5px;
            border: 0px solid transparent; 
            font-size: 12px
        }}
        
        QToolButton:hover {{
            background-color: rgba(155,155,155,{opacityLevel}); 
        }}
                        
        QToolButton:pressed {{
            background-color: rgba(128,128,128,{opacityLevel}); 
        }}
    """

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