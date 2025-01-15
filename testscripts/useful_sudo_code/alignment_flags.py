from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

def alignment_to_flags_string(alignment: Qt.Alignment):
    """Converts a Qt alignment value to a list of flag strings."""

    flags = []

    if alignment & Qt.AlignmentFlag.AlignLeft:
        flags.append("Qt.AlignLeft")
    if alignment & Qt.AlignmentFlag.AlignRight:
        flags.append("Qt.AlignRight")
    if alignment & Qt.AlignmentFlag.AlignHCenter:
        flags.append("Qt.AlignHCenter")
    if alignment & Qt.AlignmentFlag.AlignTop:
        flags.append("Qt.AlignTop")
    if alignment & Qt.AlignmentFlag.AlignBottom:
        flags.append("Qt.AlignBottom")
    if alignment & Qt.AlignmentFlag.AlignVCenter:
        flags.append("Qt.AlignVCenter")

    return flags

def orientations_to_orientation_list_string(orientation: Qt.Orientations):
    flags = []
    if orientation & Qt.Orientation.Horizontal:
        flags.append("Qt.Orientation.Horizontal")
    if orientation & Qt.Orientation.Vertical:
        flags.append("Qt.Orientation.Vertical")

    return flags