"""UI styling utilities and color constants."""

from PyQt5.QtGui import QColor

from .data_manager import load_common_config

def _make_name_button_style(bg_color, text_color, border="none"):
    """Generate a name button stylesheet."""
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
    """ + BUTTON_STATES

def _make_collapse_button_style(bg_color):
    """Generate a collapse button stylesheet."""
    return f"""
        QPushButton {{
            background-color: {bg_color};
            border: none;
            border-radius: 2px;
        }}
    """ + BUTTON_STATES

# Theme color constants
DOCKER_BUTTON_BG = "#63666a"
DOCKER_BUTTON_TEXT = "#000000"
DOCKER_BUTTON_FONT_SIZE = "10px"
GRID_NAME_COLOR = "#979797"
SELECTION_HIGHLIGHT = "#46aaff"
DARK_BG = "#2b2b2b"
PANEL_BG = "#474747"
BORDER_COLOR = "#555"
BORDER_HOVER = "#777"
BORDER_PRESSED = "#333"

# Common hover/pressed states
BUTTON_STATES = """
    QPushButton:hover { background-color: rgba(0, 0, 0, 0.3); }
    QPushButton:pressed { background-color: rgba(0, 0, 0, 0.5); }
"""

SELECTED_WIDGET_STYLE = f"""QWidget {{border: 2px solid {SELECTION_HIGHLIGHT};background-color: #474747;}}"""

COLLAPSE_BUTTON_STYLE = """
    QPushButton {
        background-color: #383838;
        border: none;
        border-radius: 2px;
    }
    QPushButton:hover { background-color: rgba(0, 0, 0, 0.3); }
    QPushButton:pressed { background-color: rgba(0, 0, 0, 0.5); }
"""
ACTIVE_COLLAPSE_BUTTON_STYLE = _make_collapse_button_style(DARK_BG)
INACTIVE_COLLAPSE_BUTTON_STYLE = _make_collapse_button_style("#383838")
SELECTED_COLLAPSE_BUTTON_STYLE = _make_collapse_button_style(DARK_BG)

NAME_BUTTON_STYLE = """
    QPushButton {
        background-color: #383838;
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        border: none;
        border-radius: 2px;
        text-align: left;
        padding: 2px 4px;
    }
    QPushButton:hover { background-color: rgba(0, 0, 0, 0.3); }
    QPushButton:pressed { background-color: rgba(0, 0, 0, 0.5); }
"""
ACTIVE_NAME_BUTTON_STYLE = _make_name_button_style(DARK_BG, SELECTION_HIGHLIGHT)
INACTIVE_NAME_BUTTON_STYLE = _make_name_button_style("#383838", GRID_NAME_COLOR)
SELECTED_NAME_BUTTON_STYLE = _make_name_button_style(DARK_BG, SELECTION_HIGHLIGHT, f"2px solid {SELECTION_HIGHLIGHT}")



def lighten_color(hex_color, amount):
    """Lighten a hex color by adjusting its HSV value."""
    try:
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        color.setHsv(h, s, min(255, v + amount), a)
        return color.name()
    except Exception:
        return hex_color

def darken_color(hex_color, amount):
    """Darken a hex color by adjusting its HSV value."""
    try:
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        color.setHsv(h, s, max(0, v - amount), a)
        return color.name()
    except Exception:
        return hex_color

def docker_btn_style():
    """Generate stylesheet for docker buttons."""
    return f"""
        QPushButton {{
            background-color: {DOCKER_BUTTON_BG}; 
            color: {DOCKER_BUTTON_TEXT}; 
            font-size: {DOCKER_BUTTON_FONT_SIZE};
            border-radius: 6px;
            border: 1px solid {BORDER_COLOR};
            padding: 3px 6px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {lighten_color(DOCKER_BUTTON_BG, 15)};
            border: 1px solid {BORDER_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {darken_color(DOCKER_BUTTON_BG, 15)};
            border: 1px solid {BORDER_PRESSED};
        }}
    """

def shortcut_btn_style():
    """Generate stylesheet for shortcut buttons from config."""
    config = load_common_config()
    color = config.color.shortcut_button_background_color
    font_color = config.color.shortcut_button_font_color
    font_size = config.font.shortcut_button_font_size
    return f"background-color: {color}; color: {font_color}; font-size: {font_size};"