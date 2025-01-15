from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *
from touchify.src.components.touchify.canvas.NtCanvas import NtCanvas

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
allow_mods = True

qwin = Krita.instance().activeWindow().qwindow()
wobj = qwin.findChild(QMdiArea)
canvas = wobj.findChild(NtCanvas)
if canvas:
    widget_layout_space = canvas.canvasLayout
    print(f'Size: {widget_layout_space.columnCount()},{widget_layout_space.rowCount()}')
    print('--------')
    for i in range(0, widget_layout_space.count()):
        row, column, rowspan, columnspan = widget_layout_space.getItemPosition(i)
        item = widget_layout_space.itemAt(i)
        expandingDirections = orientations_to_orientation_list_string(item.expandingDirections())
        alignment = alignment_to_flags_string(item.alignment())
        
        print(f'Item: {item}')
        print(f'Alignment: {alignment}')
        print(f'Expanding: {expandingDirections}')
        print(f'Position: {column},{row}')
        print(f'Span: {columnspan},{rowspan}')


        if allow_mods:
            print('Starting Mods...')
            widget_layout_space.setRowStretch(i, 0)
            widget_layout_space.setColumnStretch(i, 1)


