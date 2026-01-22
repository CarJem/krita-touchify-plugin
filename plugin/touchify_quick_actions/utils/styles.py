"""UI styling utilities and color constants."""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class Stylemap:
    def __init__(self):
        self.__DynamicColors()

    def __DynamicColors(self):
        palette = qApp.palette()

        self.SELECTED_WIDGET_BORDER = palette.highlight().color().name()
        self.SELECTED_WIDGET_BACKGROUND = palette.base().color().name()

        self.COLLAPSE_BUTTON_BACKGROUND = palette.window().color().darker(120).name()
        self.COLLAPSE_BUTTON_ACTIVE_BACKGROUND = palette.window().color().darker(150).name()
        self.COLLAPSE_BUTTON_INACTIVE_BACKGROUND = palette.window().color().darker(120).name()
        self.COLLAPSE_BUTTON_SELECTED_BACKGROUND = palette.window().color().darker(150).name()

        self.NAME_BUTTON_BACKGROUND = palette.window().color().darker(120).name()
        self.NAME_BUTTON_ACTIVE_BACKGROUND = palette.window().color().darker(150).name()
        self.NAME_BUTTON_INACTIVE_BACKGROUND = palette.window().color().darker(120).name()
        self.NAME_BUTTON_SELECTED_BACKGROUND = palette.window().color().darker(150).name()

        self.NAME_BUTTON_TEXT_COLOR = palette.text().color().name()
        self.NAME_BUTTON_ACTIVE_TEXT_COLOR = palette.highlight().color().lighter(125).name()
        self.NAME_BUTTON_INACTIVE_TEXT_COLOR = palette.placeholderText().color().name()
        self.NAME_BUTTON_SELECTED_TEXT_COLOR = palette.highlight().color().lighter(125).name()

        self.INLINE_RENAME_TEXT_COLOR = palette.text().color().name()
        self.INLINE_RENAME_BACKGROUND = palette.window().color().darker(120).name()

        self.TITLEBAR_ICON_COLOR = palette.dark().color().name()

        self.DRAGGABLE_GRID_BUTTON_BG_COLOR = palette.base().color().name()
        self.DRAGGABLE_GRID_BUTTON_TEXT_COLOR = palette.text().color().name()
        self.DRAGGABLE_GRID_BUTTON_BG_HOVER_COLOR = palette.base().color().darker(120).name()

        self.DRAGGABLE_GRID_BUTTON_BACKGROUND = "transparent"
        self.DRAGGABLE_GRID_BUTTON_BACKGROUND_HOVERED = palette.mid().color().name()
        self.DRAGGABLE_GRID_BUTTON_BACKGROUND_PRESSED = palette.midlight().color().name()

        self.DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND = palette.highlight().color().name()
        self.DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND_HOVERED = palette.highlight().color().lighter(120).name()
        self.DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND_PRESSED = palette.highlight().color().darker(120).name()

    def __OriginalColors(self):
        self.SELECTED_WIDGET_BORDER = "#46aaff"
        self.SELECTED_WIDGET_BACKGROUND = "#474747"

        self.COLLAPSE_BUTTON_BACKGROUND = "#383838"
        self.COLLAPSE_BUTTON_ACTIVE_BACKGROUND = "#2b2b2b"
        self.COLLAPSE_BUTTON_INACTIVE_BACKGROUND = "#383838"
        self.COLLAPSE_BUTTON_SELECTED_BACKGROUND = "#2b2b2b"

        self.NAME_BUTTON_BACKGROUND = "#383838"
        self.NAME_BUTTON_ACTIVE_BACKGROUND = "#2b2b2b"
        self.NAME_BUTTON_INACTIVE_BACKGROUND = "#383838"
        self.NAME_BUTTON_SELECTED_BACKGROUND = "#2b2b2b"

        self.NAME_BUTTON_TEXT_COLOR = "#ffffff"
        self.NAME_BUTTON_ACTIVE_TEXT_COLOR = "#46aaff"
        self.NAME_BUTTON_INACTIVE_TEXT_COLOR = "#979797"
        self.NAME_BUTTON_SELECTED_TEXT_COLOR = "#46aaff"

        self.INLINE_RENAME_TEXT_COLOR = "#979797"
        self.INLINE_RENAME_BACKGROUND = "#383838"

        self.TITLEBAR_ICON_COLOR = "#474747"

        self.DRAGGABLE_GRID_BUTTON_BG_COLOR = "#383838"
        self.DRAGGABLE_GRID_BUTTON_TEXT_COLOR = "#d2d2d2"
        self.DRAGGABLE_GRID_BUTTON_BG_HOVER_COLOR = "#282828"

        self.DRAGGABLE_GRID_BUTTON_BACKGROUND = "transparent"
        self.DRAGGABLE_GRID_BUTTON_BACKGROUND_HOVERED = "palette(mid)"
        self.DRAGGABLE_GRID_BUTTON_BACKGROUND_PRESSED = "palette(midlight)"

        self.DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND = "palette(highlight)" #self.palette().highlight().color()
        self.DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND_HOVERED = "palette(highlight)" #hl.lighter(120).name()
        self.DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND_PRESSED = "palette(highlight)" #hl.darker(120).name()


    @staticmethod
    def instance(reload=False) -> "Stylemap":
        global cached_data
        if 'cached_data' not in globals() or not isinstance(cached_data, Stylemap) or reload == True:
            cached_data = Stylemap()
        return cached_data


@staticmethod
def SM(): return Stylemap.instance()

@staticmethod
def PAGE_TAB_BUTTON_STYLE():
    bg_color = SM().SELECTED_WIDGET_BACKGROUND
    text_color = SM().NAME_BUTTON_TEXT_COLOR

    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            font-weight: bold;
            font-size: 12px;
            border: 2px solid {SM().SELECTED_WIDGET_BACKGROUND};
            border-radius: 4px;
            padding: 4px 4px;
            margin-top: 2px;
            margin-bottom: 2px;
        }}
        QPushButton:checked {{ border: 2px solid {SM().NAME_BUTTON_SELECTED_TEXT_COLOR}; }}
        QPushButton:hover {{ background-color: rgba(0, 0, 0, 0.3); }}
        QPushButton:pressed {{ background-color: rgba(0, 0, 0, 0.5); }}
    """

@staticmethod
def COLLAPSE_BUTTON_STYLE(bg_color: str = None):
    if not bg_color: bg_color = SM().COLLAPSE_BUTTON_BACKGROUND
    return f"""
        QPushButton {{
            background-color: {bg_color};
            border: none;
            border-radius: 2px;
        }}
        QPushButton:hover {{ background-color: rgba(0, 0, 0, 0.3); }}
        QPushButton:pressed {{ background-color: rgba(0, 0, 0, 0.5); }}
    """
@staticmethod
def ACTIVE_COLLAPSE_BUTTON_STYLE(): 
    return COLLAPSE_BUTTON_STYLE(SM().COLLAPSE_BUTTON_ACTIVE_BACKGROUND)
@staticmethod
def INACTIVE_COLLAPSE_BUTTON_STYLE(): 
    return COLLAPSE_BUTTON_STYLE(SM().COLLAPSE_BUTTON_INACTIVE_BACKGROUND)
@staticmethod
def SELECTED_COLLAPSE_BUTTON_STYLE(): 
    return COLLAPSE_BUTTON_STYLE(SM().COLLAPSE_BUTTON_SELECTED_BACKGROUND)

@staticmethod
def NAME_BUTTON_STYLE(bg_color=None, text_color=None, border=None):
    """Generate a name button stylesheet."""
    if not bg_color: bg_color = SM().NAME_BUTTON_BACKGROUND
    if not text_color: text_color = SM().NAME_BUTTON_TEXT_COLOR
    if not border: border = "none"

    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            font-weight: bold;
            font-size: 12px;
            border: {border};
            border-radius: 2px;
            text-align: left;
            padding: 2px 4px;
        }}
        QPushButton:hover {{ background-color: rgba(0, 0, 0, 0.3); }}
        QPushButton:pressed {{ background-color: rgba(0, 0, 0, 0.5); }}
    """
@staticmethod
def ACTIVE_NAME_BUTTON_STYLE():
    return NAME_BUTTON_STYLE(SM().NAME_BUTTON_ACTIVE_BACKGROUND, SM().NAME_BUTTON_ACTIVE_TEXT_COLOR)
@staticmethod
def INACTIVE_NAME_BUTTON_STYLE():
    return NAME_BUTTON_STYLE(SM().NAME_BUTTON_INACTIVE_BACKGROUND, SM().NAME_BUTTON_INACTIVE_TEXT_COLOR)
@staticmethod
def SELECTED_NAME_BUTTON_STYLE():
    return NAME_BUTTON_STYLE(SM().NAME_BUTTON_SELECTED_BACKGROUND, SM().NAME_BUTTON_SELECTED_TEXT_COLOR, f"2px solid {SM().NAME_BUTTON_SELECTED_TEXT_COLOR}")
@staticmethod
def INLINE_RENAME_EDITOR_STYLE():
    return f"""
        QLineEdit {{
            background-color: {SM().INLINE_RENAME_BACKGROUND};
            color: {SM().INLINE_RENAME_TEXT_COLOR};
            font-weight: bold;
            font-size: 12px;
            border: none;
            border-radius: 2px;
            padding: 2px 4px;
        }}
    """

@staticmethod
def MENU_ICON_BUTTON_STYLE():
    return f"""
            QPushButton {{
                background-color: {SM().TITLEBAR_ICON_COLOR};
                border: none;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.3);
            }}
        """
@staticmethod
def SELECTED_WIDGET_STYLE():
    return f"""QWidget {{border: 2px solid {SM().SELECTED_WIDGET_BORDER};background-color: {SM().SELECTED_WIDGET_BACKGROUND};}}"""
@staticmethod
def TOP_ROW_STYLE():
    return f"""
        QWidget {{
            background-color: {SM().TITLEBAR_ICON_COLOR};
        }}
    """

@staticmethod
def DRAGGABLE_GRID_BUTTON_LABEL_STYLE(font_size: str, bg_color: str):
    return f"""
            QLabel {{
                background-color: {bg_color};
                color: {SM().DRAGGABLE_GRID_BUTTON_TEXT_COLOR};
                font-size: {font_size}px;
                padding: 2px 1px;
                border: none;
            }}
        """
@staticmethod
def DRAGGABLE_GRID_BUTTON_ICON_STYLE(bg_color: str):
    return f"""
            QToolButton {{
                padding: 4px;
                border: none;
                background-color: {bg_color}
            }}
        """
@staticmethod
def DRAGGABLE_GRID_BUTTON_BACKGROUND_COLOR(pressed: bool, selected: bool, hovered: bool):
    if selected:
        if pressed: return SM().DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND_PRESSED
        elif hovered: return SM().DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND_HOVERED
        else: return SM().DRAGGABLE_GRID_BUTTON_SELECTED_BACKGROUND
    elif pressed: return SM().DRAGGABLE_GRID_BUTTON_BACKGROUND_PRESSED
    elif hovered: return SM().DRAGGABLE_GRID_BUTTON_BACKGROUND_HOVERED
    else: return SM().DRAGGABLE_GRID_BUTTON_BACKGROUND