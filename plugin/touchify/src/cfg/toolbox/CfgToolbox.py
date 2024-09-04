import string
from .CfgToolboxItem import *
from .CfgToolboxCategory import *
from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions


   
class CfgToolbox:
    categories: TypedList[CfgToolboxCategory] = [] 
    menuDelay: int = 200
    submenuButton: bool = False

    column_count: int = 2
    icon_size: int = 16

    presetName: str = "New Toolbox Preset"


    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

        categories = Extensions.default_assignment(args, "categories", [])
        self.categories = Extensions.list_assignment(categories, CfgToolboxCategory)

    def __str__(self):
        return self.presetName.replace("\n", "\\n")

    def getFileName(self):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in self.presetName if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename.lower()
    
    def forceLoad(self):
        self.categories = TypedList(self.categories, CfgToolboxCategory)

    def propertygrid_labels(self):
        labels = {}
        labels["categories"] = "Categories"
        labels["items"] = "Items"
        labels["menuDelay"] = "Menu Delay"
        labels["submenuButton"] = "Submenu Button"
        labels["column_count"] = "Column Count"
        labels["icon_size"] = "Icon Size"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["column_count"] = {"type": "range", "min": 1}
        return restrictions
    
    def loadDefaults(self):
        result = TypedList([], CfgToolboxCategory)

        vectorSection = CfgToolboxCategory()
        vectorSection.id = "Vector"

        vectorSection.addAction("InteractionTool")
        vectorSection.addAction("SvgTextTool")
        vectorSection.addAction("PathTool")
        vectorSection.addAction("KarbonCalligraphyTool")

        paintSection = CfgToolboxCategory()
        paintSection.id = "Paint"

        paintSection.addAction("KisToolPencil")
        paintSection.addAction("KritaShape/KisToolLine")
        paintSection.addAction("KritaShape/KisToolRectangle")
        paintSection.addAction("KritaShape/KisToolEllipse")
        paintSection.addAction("KisToolPolygon")
        paintSection.addAction("KisToolPolyline")
        paintSection.addAction("KisToolPath")
        paintSection.addAction("KritaShape/KisToolBrush")
        paintSection.addAction("KritaShape/KisToolDyna")
        paintSection.addAction("KritaShape/KisToolMultiBrush")

        transformSection = CfgToolboxCategory()
        transformSection.id = "Transform"

        transformSection.addAction("KisToolTransform")
        transformSection.addAction("KritaTransform/KisToolMove")
        transformSection.addAction("KisToolCrop")


        colorSection = CfgToolboxCategory()
        colorSection.id = "Color"

        colorSection.addAction("KritaFill/KisToolGradient")
        colorSection.addAction("KritaSelected/KisToolColorSampler")
        colorSection.addAction("KritaShape/KisToolLazyBrush")
        colorSection.addAction("KritaShape/KisToolSmartPatch")
        colorSection.addAction("KritaFill/KisToolFill")
        colorSection.addAction("KisToolEncloseAndFill")

        measureSection = CfgToolboxCategory()
        measureSection.id = "Measure"

        measureSection.addAction("KisAssistantTool")
        measureSection.addAction("KritaShape/KisToolMeasure")
        measureSection.addAction("ToolReferenceImages")

        selectSection = CfgToolboxCategory()
        selectSection.id = "Select"

        selectSection.addAction("KisToolSelectRectangular")
        selectSection.addAction("KisToolSelectElliptical")
        selectSection.addAction("KisToolSelectPolygonal")
        selectSection.addAction("KisToolSelectOutline") 
        selectSection.addAction("KisToolSelectContiguous")
        selectSection.addAction("KisToolSelectSimilar")
        selectSection.addAction("KisToolSelectPath")   
        selectSection.addAction("KisToolSelectMagnetic")

        navigationSection = CfgToolboxCategory()
        navigationSection.id = "Navigation"

        navigationSection.addAction("PanTool")
        navigationSection.addAction("ZoomTool")

        result.append(vectorSection)
        result.append(transformSection)
        result.append(paintSection)
        result.append(colorSection)
        result.append(measureSection)
        result.append(selectSection)
        result.append(navigationSection)

        return result


