from krita import *
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QIcon,QPixmap
from jemlib.api_touchify.env import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.window import WindowAPI

    
def getCurrentLayer():
    doc = KritaAPI.get_active_document()
    return doc.active_node

def getCurrentDoc():
    return KritaAPI.get_active_document()

def getSelectedLayers():
    v = KritaAPI.get_active_view()
    return v.selectedNodes


# Colors for the color labels, copied from krita code in KisNodeViewColorScheme.cpp
transparentColor = QColor(Qt.transparent) #0
blueColor = QColor(91,173,220) #1
greenColor = QColor(151,202,63) #2
yellowColor = QColor(247,229,61) #3
orangeColor = QColor(255,170,63) #4
brownColor = QColor(177,102,63) #5
redColor = QColor(238,50,51) #6
purpleColor = QColor(191,106,209) #7
greyColor = QColor(118,119,114) #8

class LayerLabelBox(QComboBox):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setAccessibleName('colorLabelBox')
        self.setObjectName('colorLabelBox')
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        #self.setMinimumHeight(35)

        # generates an array to automatize the process of creating icons 
        colors = [blueColor,greenColor,yellowColor,orangeColor,brownColor,redColor,purpleColor,greyColor]

        # I dont feel like figuring out how to make a transparent button like in the color labels
        # so i am going the csp route of just making an empty square
        transparentFill = QPixmap(20,20)
        transparentFill.fill(transparentColor)
        # draws a rectangle around the transparent area
        painter = QPainter(transparentFill)
        pen = QPen()
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(0,0,20,20)
        painter.end()
        transparentIcon = QIcon(transparentFill)
        self.addItem(transparentIcon,'')

        # generates all icons 
        for color in colors:
            colorFill = QPixmap(20,20)
            colorFill.fill(color)
            colorIcon = QIcon(colorFill)
            self.addItem(colorIcon,'')
            
        self.activated.connect(lambda index: self.updateLayerColorLabel(index))

    def setInstance(self, window: WindowAPI):
        self.notifier = window.notifier
        self.notifier.selectedNodeColorsChanged.connect(self.updateInterface)
        self.updateInterface()
        
    def showEvent(self, event):
        super().showEvent(event)

    def hideEvent(self, event):
        super().hideEvent(event)
        
    def closeEvent(self, event):
        super().closeEvent(event)

    def updateInterface(self):
        if self.isVisible() == False:
            return
        
        selectedLayers = getSelectedLayers()

        if len(selectedLayers) == 0:
            currentLayer = getCurrentLayer()
            if currentLayer == None: return
            self.setCurrentIndex(currentLayer.color_label)
        else:
            selected_index = -1
            are_same = True
            for layer in selectedLayers:
                current_label_index = layer.color_label
                if selected_index == -1:
                    selected_index = current_label_index
                elif selected_index != current_label_index:
                    are_same = False
                    break
            
            if are_same and selected_index != -1:
                self.setCurrentIndex(selected_index)
            else:
                self.setCurrentIndex(0)



    def updateLayerColorLabel(self, index):
        selectedLayers = getSelectedLayers()
        if len(selectedLayers) == 0:
            currentLayer = getCurrentLayer()
            if currentLayer != None: currentLayer.color_label = index
        else:
            for layer in selectedLayers:
                layer.color_label = index

