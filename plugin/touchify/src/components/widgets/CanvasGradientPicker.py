
from krita import *
from PyQt5.QtCore import *
from xml.dom.minidom import parse as xmlParse

from touchify.src.components.common.painters.CheckerPainter import CheckerPainter
from touchify.__env__ import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class GradientLoader:

    class GradientData:
        def __init__(self, args: dict[str, any]):
            self.leftEndpointCoordinate: float = args["leftEndpointCoordinate"]
            self.midpointCoordinate: float = args["midpointCoordinate"]
            self.rightEndpointCoordinate: float = args["rightEndpointCoordinate"]
            self.prevColorR: float = args["prevColorR"]
            self.prevColorG: float = args["prevColorG"]
            self.prevColorB: float = args["prevColorB"]
            self.prevAlpha: float = args["prevAlpha"]
            self.colorR: float = args["colorR"]
            self.colorG: float = args["colorG"]
            self.colorB: float = args["colorB"]
            self.alpha: float = args["alpha"]
            self.interpolation: int = args["interpolation"]
            self.coloringType: int = args["coloringType"]

    def __init__(self):
        pass

    def ForegroundToBackground(alpha: bool = False):
        return [
            GradientLoader.GradientData({
                'leftEndpointCoordinate':0,
                'midpointCoordinate':0,
                'rightEndpointCoordinate':0,
                'prevColorR':0,
                'prevColorG':0,
                'prevColorB':0,
                'prevAlpha':1,
                'colorR':0,
                'colorG':0,
                'colorB':0,
                'alpha':1,
                'interpolation':0,
                'coloringType':0,      
            }),
            GradientLoader.GradientData({
                'leftEndpointCoordinate':1,
                'midpointCoordinate':1,
                'rightEndpointCoordinate':1,
                'prevColorR':0,
                'prevColorG':0,
                'prevColorB':0,
                'prevAlpha':1,
                'colorR':0 if alpha else 1,
                'colorG':0 if alpha else 1,
                'colorB':0 if alpha else 1,
                'alpha': 0 if alpha else 1,
                'interpolation':0,
                'coloringType':0,      
            })
        ]

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return list(float(int(value[i:i + lv // 3], 16))/255 for i in range(0, lv, lv // 3))

    def cssStyleAttribute(self, css_definition, css_attribute):
        css_definition = css_definition.replace(' ','') #strip spaces
        start_index = css_definition.find(css_attribute) #find start of the css attribute
        if start_index == -1:
            return ''
        else:
            end_index = css_definition.find(';',start_index) #find ending comma or -1
            searched_attrib = css_definition[start_index:end_index] #searched attrib
            searched_value = searched_attrib.split(':')[1] #searched value
            return searched_value

    def getSvgAttribute(self, node,attribute):
        result = node.getAttribute(attribute)
        if result in (None,'',' '): #if the attribute was not found, try find it as a style attribute value
            style = node.getAttribute('style')
            result = self.cssStyleAttribute(style,attribute)
            return result
        else:
            return result

    def svg2gradient(self, filepath, use_alpha = True) -> list[GradientData]:
        n = 0

        f = open(filepath,'r')
        svg = f.read()
        f.close()
        
        try:
            domData = xmlParse(svg)
        except:
            return []
        
        linearGradient = domData.getElementsByTagName('linearGradient')[0]
        
        gradientData = []
        
        for stop in linearGradient.getElementsByTagName('stop'):
            #print("ELEMENT "+str(n))
            n+=1
            if n == 1:
                color_string = self.getSvgAttribute(stop,'stop-color')
                    
                if color_string[0] == '#':
                    #tuple(ord(c) for c in color_string[1:].decode('hex'))
                    #struct.unpack('BBB',color_string[1:].decode('hex'))
                    prevColor = self.hex_to_rgb(color_string)
                    #print(str(color))
                else:
                    prevColor = list(float(c)/255 for c in color_string.replace('rgb(','').replace(')','').split(','))
                prevColor.append(1.0)
                prevColor = tuple(prevColor)
                    
                if use_alpha:
                    opacity = self.getSvgAttribute(stop,'stop-opacity')
                    if opacity == '':
                        prevAlpha = 1.0
                    else:
                        prevAlpha = float(opacity)
                else:
                    prevAlpha = 1.0
                prevStop = 0.0
                #prevColor = list(float(c)/255 for c in stop.getAttribute('stop-color').replace('rgb(','').replace(')','').split(','))
                prevColorR = prevColor[0]
                prevColorG = prevColor[1]
                prevColorB = prevColor[2]
                #if use_alpha:
                #    prevAlpha = float(stop.getAttribute('stop-opacity'))
                #else:
                #    prevAlpha = 1.0
            else:
                leftEndpointCoordinate = prevStop
                rightEndpointCoordinate = float(stop.getAttribute('offset').split('%')[0])/100.0
                #midpointCoordinate = leftEndpointCoordinate+((rightEndpointCoordinate-leftEndpointCoordinate)/2)
                midpointCoordinate = -1.0 #no point in creating
                #color = list(float(c)/255 for c in stop.getAttribute('stop-color').replace('rgb(','').replace(')','').split(','))
                color_string = self.getSvgAttribute(stop,'stop-color')

                if color_string[0] == '#':
                    #tuple(ord(c) for c in color_string[1:].decode('hex'))
                    #struct.unpack('BBB',color_string[1:].decode('hex'))
                    color =  self.hex_to_rgb(color_string)
                    #print(str(color))
                else:
                    color = list(float(c)/255 for c in color_string.replace('rgb(','').replace(')','').split(','))
                color.append(1.0)
                color = tuple(color)
                    
                if use_alpha:
                    opacity = self.getSvgAttribute(stop,'stop-opacity')
                    
                    if opacity == '':
                        alpha = 1
                    else:
                        alpha = float(opacity)
                else:
                    alpha = 1.0
                    
                colorR = color[0]
                colorG = color[1]
                colorB = color[2]
    ##            if use_alpha:
    ##                alpha = float(stop.getAttribute('stop-opacity'))
    ##            else:
    ##                alpha = 1.0
                gradientData.append(
                    GradientLoader.GradientData({
                        'leftEndpointCoordinate':leftEndpointCoordinate,
                        'midpointCoordinate':midpointCoordinate,
                        'rightEndpointCoordinate':rightEndpointCoordinate,
                        'prevColorR':prevColorR,
                        'prevColorG':prevColorG,
                        'prevColorB':prevColorB,
                        'prevAlpha':prevAlpha,
                        'colorR':colorR,
                        'colorG':colorG,
                        'colorB':colorB,
                        'alpha':alpha,
                        'interpolation':0,
                        'coloringType':0,
                    })
                )

                prevStop = rightEndpointCoordinate
                prevColorR = colorR
                prevColorG = colorG
                prevColorB = colorB
                prevAlpha = alpha
        domData.unlink()        
        return gradientData
                
    def ggr2gradient(self, filepath, use_alpha = True, color_fg = [1,1,1], color_bg = [0,0,0]) -> list[GradientData]:
        
        f = open(filepath,'r')
        ggr = f.read()
        f.close()
        
        ggr_input = ggr.splitlines()
        if ggr_input[0] == 'GIMP Gradient':
            gradientName = ggr_input[1].replace('Name: ','')
            gradientDataTmp = [f.split() for f in ggr_input[3:3+int(ggr_input[2])]]
            gradientData = []
            for row in gradientDataTmp:
                #print(str(len(row)))
                if use_alpha:
                    alpha = float(row[10])
                    prevAlpha = float(row[6])
                else:
                    alpha = 1.0
                    prevAlpha = 1.0
                if len(row) == 15: #if there are foreground/background definitions for the row (segment) stops
                    #print("14")
                    if row[13] != '0': #first stop
                        if row[13] in ('1','2'): #foreground color
                            row[3] = color_fg[0]
                            row[4] = color_fg[1]
                            row[5] = color_fg[2]
                        elif row[13] in ('3','4'): #background color
                            row[3] = color_bg[0]
                            row[4] = color_bg[1]
                            row[5] = color_bg[2]
                        if row[13] in ('2','4'):
                            prevAlpha = 0.0
                    if row[14] != '0':
                        if row[14] in ('1','2'): #foreground color
                            row[7] = color_fg[0]
                            row[8] = color_fg[1]
                            row[9] = color_fg[2]
                        elif row[14] in ('3','4'): #background color
                            row[7] = color_bg[0]
                            row[8] = color_bg[1]
                            row[9] = color_bg[2]
                        if row[14] in ('2','4'):
                            prevAlpha = 0.0
                if float(row[1]) != (float(row[0])+((float(row[0]) - float(row[2]))/2.0)):
                    midpointCoordinate = float(row[1])
                else:
                    midpointCoordinate = -1

                data = GradientLoader.GradientData({
                    'leftEndpointCoordinate':float(row[0]),
                    'midpointCoordinate': midpointCoordinate,
                    'rightEndpointCoordinate':float(row[2]),
                    'prevColorR':float(row[3]),
                    'prevColorG':float(row[4]),
                    'prevColorB':float(row[5]),
                    'prevAlpha':prevAlpha,
                    'colorR':float(row[7]),
                    'colorG':float(row[8]),
                    'colorB':float(row[9]),
                    'alpha':alpha,
                    'interpolation':int(row[11]),
                    'coloringType':int(row[12]),
                })
                gradientData.append(data)
            return gradientData
        

class CanvasGradientPicker(QPushButton):

    def __init__(self, parent: QWidget | None = None):
        super(CanvasGradientPicker, self).__init__(parent)
        self.clicked.connect(self.openBrushPicker)

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.appEngine.mgr_actions.gradientChanged.connect(self.onGradientChanged)
        self.onGradientChanged(self.appEngine.mgr_actions.getCurrentGradient())

    def openBrushPicker(self):
        self.appEngine.mgr_actions.Create_Popup("gradient_chooser_popup", self)
    
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)

    def updateIcon(self):
        if self.gradient:
            file_name = self.gradient.filename()
            if file_name == "Foreground to Background.svg":
                data = GradientLoader.ForegroundToBackground()
            elif file_name == "Foreground to Transparent.svg":
                data = GradientLoader.ForegroundToBackground(True)
            else:
                resource_directory = Krita.instance().getAppDataLocation()
                file_path = os.path.join(resource_directory, "gradients", file_name)
                data = []

                try:
                    if file_name.endswith("ggr"):
                        data = GradientLoader().ggr2gradient(file_path)
                    elif file_name.endswith("svg"):
                        data = GradientLoader().svg2gradient(file_path)
                    else:
                        data = []
                except:
                    data = []
        else:
            data = []

        linear_gradient = QLinearGradient(self.rect().bottomLeft(), self.rect().bottomRight())
        for section in data:
            prevColor = QColor(round(section.prevColorR * 255), 
                            round(section.prevColorG * 255), 
                            round(section.prevColorB * 255), 
                            round(section.prevAlpha * 255))
            
            color = QColor(round(section.colorR * 255), 
                        round(section.colorG * 255), 
                        round(section.colorB * 255), 
                        round(section.alpha * 255))
            
            linear_gradient.setColorAt(section.leftEndpointCoordinate, prevColor)
            linear_gradient.setColorAt(section.rightEndpointCoordinate, color)


        transparent_background = CheckerPainter(4)

        pixmap = QPixmap(self.width(), self.height())

        canvas = QPainter(pixmap)
        transparent_background.paint(canvas, pixmap.rect(), pixmap.rect().topLeft())
        canvas.fillRect(self.rect(), linear_gradient)       
        canvas.end()

        if pixmap: self.setIcon(QIcon(pixmap))

    def resizeEvent(self, a0: QResizeEvent):
        self.setIconSize(a0.size().shrunkBy(QMargins(4,4,4,4)))
        self.updateIcon()
        return super().resizeEvent(a0)

    def onGradientChanged(self, current_gradient: Resource):
        self.gradient = current_gradient
        self.updateIcon()