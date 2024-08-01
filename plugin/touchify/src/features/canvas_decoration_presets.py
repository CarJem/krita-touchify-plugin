

from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from ..ext.KritaSettings import *
from ..ext.extensions_json import *
from ..ext.extensions_krita import *
from touchify.src import stylesheet
import json
import copy

from ..components.krita_ext.KisSliderSpinBox import KisSliderSpinBox
from ..components.krita_ext.KisAngleSelector import KisAngleSelector
from ..components.ColorButton import ColorButton

class CanvasDecorationsPreset(QObject):
    def __init__(self):
        super().__init__()
        self.presetName = "New Preset"
        
        self.checkers_main_color: KS_Color = KS_Color()
        self.checkers_alt_color: KS_Color = KS_Color()
        self.checkers_size: int = 32
        self.checkers_enabled: bool = False
        
        self.pixgrid_color: KS_Color = KS_Color(255, 255, 255)
        self.pixgrid_threshold: float = 24
        self.pixgrid_enabled: bool = False
        
        self.selection_outline_opacity: float = 1.0
        self.selection_overlay_color: KS_Color = KS_Color(255, 0, 0)
        self.selection_overlay_opacity: float = 0.5
        self.selection_enabled: bool = False
        
        self.border_color: KS_Color = KS_Color(128, 128, 128)
        self.border_enabled: bool = False
             
    def loads(self, _dict: dict[str, any]):
        if _dict is not None:
            for key, value in _dict.items():
                if hasattr(self, key):
                    if type(getattr(self, key)) == type(value):
                        setattr(self, key, value)
                    elif isinstance(getattr(self, key), KS_Color):
                        setattr(self, key, KS_Color(value["r"], value["g"], value["b"]))
                               
    def activate(self): 
        if self.checkers_enabled:
            KritaSettings.writeSettingColor("", "checkerscolor", self.checkers_main_color)
            KritaSettings.writeSettingColor("", "checkerscolor2", self.checkers_alt_color)
            KritaSettings.writeSettingInt("", "checkSize", self.checkers_size)
            
        if self.pixgrid_enabled:
            KritaSettings.writeSettingColor("", "pixelGridColor", self.pixgrid_color)
            KritaSettings.writeSettingFloat("", "pixelGridDrawingThreshold", self.pixgrid_threshold)
        
        if self.selection_enabled:
            KritaSettings.writeSettingFloat("", "selectionOutlineOpacity", self.selection_outline_opacity)
            KritaSettings.writeSettingColor("", "selectionOverlayMaskColor", self.selection_overlay_color.setOpacityFloat(self.selection_overlay_opacity))
        
        if self.border_enabled:
            KritaSettings.writeSettingColor("", "canvasBorderColor", self.border_color)
        
    def current():
        result = CanvasDecorationsPreset()
        
        result.checkers_main_color = KritaSettings.readSettingColor("", "checkerscolor", KS_Color())
        result.checkers_alt_color = KritaSettings.readSettingColor("", "checkerscolor2", KS_Color())
        result.checkers_size = KritaSettings.readSettingInt("", "checkSize", 32)
            
        result.pixgrid_color = KritaSettings.readSettingColor("", "pixelGridColor", KS_Color(255, 255, 255))
        result.pixgrid_threshold = KritaSettings.readSettingFloat("", "pixelGridDrawingThreshold", 24)
        
        result.selection_outline_opacity = KritaSettings.readSettingFloat("", "selectionOutlineOpacity", 1.0)
        
        selection_overlay: KS_AlphaColor = KritaSettings.readSettingAlphaColor("", "selectionOverlayMaskColor", KS_AlphaColor(255,0,0,128))
        result.selection_overlay_color = selection_overlay.noAlpha()
        result.selection_overlay_opacity = selection_overlay.getOpacityFloat()
        
        result.border_color = KritaSettings.readSettingColor("", "canvasBorderColor", KS_Color(128, 128, 128))
    
        return result
    
class CanvasDecorationsConfig:
    def __init__(self):
        self.canvas_presets: dict[int, CanvasDecorationsPreset] = dict()
        self.load()
        
        
    def load(self):
        self.canvas_presets = dict()
        
        try:
            json_data = KritaSettings.readSetting("CanvasDecorationsPresets", "Presets", "[]")
            json_object = json.loads(json_data)
            
            index = 0

            if isinstance(json_object, list):
                json_list: list = json_object
                for dict_item in json_list:
                    if isinstance(dict_item, dict):
                        presetItem = CanvasDecorationsPreset()
                        presetItem.loads(dict_item)
                        self.canvas_presets[str(index)] = presetItem
                        index += 1
        except:
            pass
                
    def save(self):
        json_str = json.dumps(list(self.canvas_presets.values()), default=vars)
        KritaSettings.writeSetting("CanvasDecorationsPresets", "Presets", json_str)
        self.load()

class CanvasDecorationsEditor(QDialog):
    def __init__(self, preset: CanvasDecorationsPreset, parent: QWidget | None = None):
        super().__init__(parent)
        self.accepted.connect(self.updatePreset)
        self.preset: CanvasDecorationsPreset = preset
        self.setupComponents()
        
    def updatePreset(self):
        self.preset.presetName = self._presetNameEntry.text()
        
        self.preset.checkers_enabled = self._checkerboard_group.isChecked()
        self.preset.checkers_main_color = KS_Color.fromQt(self._checkerboard_color1.color())
        self.preset.checkers_alt_color = KS_Color.fromQt(self._checkerboard_color2.color())
        self.preset.checkers_size = self._checkerboard_size.value()
        
        self.preset.pixgrid_enabled = self._pixgrid_group.isChecked()
        self.preset.pixgrid_color = KS_Color.fromQt(self._pixgrid_color.color())
        self.preset.pixgrid_threshold = self._pixgrid_threshold.value()
        
        self.preset.selection_enabled = self._selection_group.isChecked()
        self.preset.selection_outline_opacity = self._selection_outline_opacity.value()
        self.preset.selection_overlay_color = KS_Color.fromQt(self._selection_overlay_color.color())
        self.preset.selection_overlay_opacity = self._selection_overlay_opacity.value()
        
        self.preset.border_enabled = self._checkerboard_group.isChecked()
        self.preset.border_color = KS_Color.fromQt(self._border_color.color())
        
    def setupComponents(self):
        self._gridLayout = QFormLayout(self)
        self.setLayout(self._gridLayout)
            
        self._buttonBox = QDialogButtonBox()
        self._saveBtn = self._buttonBox.addButton(QDialogButtonBox.StandardButton.Save)
        self._saveBtn.clicked.connect(self.accept)
        self._cancelBtn = self._buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._cancelBtn.clicked.connect(self.reject)
        
        self._presetNameEntry = QLineEdit()
        self._presetNameEntry.setText(self.preset.presetName)
        
        
        
        #region Checkerboard
        self._checkerboard_group = QGroupBox(self)
        self._checkerboard_group.setCheckable(True)
        self._checkerboard_group.setChecked(self.preset.checkers_enabled)
        self._checkerboard_group.setTitle("Transparency Checkerboard:")
        self._checkerboard_layout = QFormLayout(self._checkerboard_group)     
        self._checkerboard_color1 = ColorButton(self, self.preset.checkers_main_color.toQt())
        self._checkerboard_color2 = ColorButton(self, self.preset.checkers_alt_color.toQt())
        self._checkerboard_size = QSpinBox(self)
        self._checkerboard_size.setMinimum(0)
        self._checkerboard_size.setMaximum(256)
        self._checkerboard_size.setSuffix(" px")
        self._checkerboard_size.setValue(self.preset.checkers_size)    
        self._checkerboard_layout.addRow("Color 1: ", self._checkerboard_color1)
        self._checkerboard_layout.addRow("Color 2: ", self._checkerboard_color2)
        self._checkerboard_layout.addRow("Size: ", self._checkerboard_size)
        self._checkerboard_group.setLayout(self._checkerboard_layout)
        #endregion
        
        #region Pixel Grid
        self._pixgrid_group = QGroupBox(self)
        self._pixgrid_group.setCheckable(True)
        self._pixgrid_group.setChecked(self.preset.pixgrid_enabled)
        self._pixgrid_group.setTitle("Selection Overlay:")
        self._pixgrid_layout = QFormLayout(self._pixgrid_group)      
        self._pixgrid_color = ColorButton(self, self.preset.pixgrid_color.toQt())       
        self._pixgrid_threshold = QDoubleSpinBox(self)
        self._pixgrid_threshold.setMinimum(0)
        self._pixgrid_threshold.setMaximum(99)
        self._pixgrid_threshold.setDecimals(2)
        self._pixgrid_threshold.setSuffix("%")
        self._pixgrid_threshold.setValue(self.preset.pixgrid_threshold)    
        self._pixgrid_layout.addRow("Color: ", self._pixgrid_color)
        self._pixgrid_layout.addRow("Start showing at: ", self._pixgrid_threshold)
        self._pixgrid_group.setLayout(self._pixgrid_layout)
        #endregion
        
        #region Selection Overlay
        self._selection_group = QGroupBox(self)
        self._selection_group.setCheckable(True)
        self._selection_group.setChecked(self.preset.selection_enabled)
        self._selection_group.setTitle("Selection Overlay:")
        self._selection_layout = QFormLayout(self._selection_group)      
        self._selection_outline_opacity = KisSliderSpinBox(0, 1, False, self)
        self._selection_outline_opacity.setValue(self.preset.selection_outline_opacity)   
        self._selection_overlay_color = ColorButton(self, self.preset.selection_overlay_color.toQt())     
        self._selection_overlay_opacity = KisSliderSpinBox(0, 1, False, self)
        self._selection_overlay_opacity.setValue(self.preset.selection_overlay_opacity)  
        self._selection_layout.addRow("Outline Opacity: ", self._selection_outline_opacity)
        self._selection_layout.addRow("Overlay Color: ", self._selection_overlay_color)
        self._selection_layout.addRow("Overlay Opacity: ", self._selection_overlay_opacity)
        self._selection_group.setLayout(self._selection_layout)
        #endregion
        
        #region Canvas Border
        self._border_group = QGroupBox(self)
        self._border_group.setCheckable(True)
        self._border_group.setChecked(self.preset.border_enabled)
        self._border_group.setTitle("Canvas Border:")
        self._border_layout = QFormLayout(self._border_group)      
        self._border_color = ColorButton(self, self.preset.border_color.toQt())       
        self._border_layout.addRow("Color: ", self._border_color)
        self._border_group.setLayout(self._border_layout)
        #endregion
        
        self._gridLayout.addRow("Preset Name:", self._presetNameEntry)
        self._gridLayout.addWidget(self._checkerboard_group)
        self._gridLayout.addWidget(self._border_group)
        self._gridLayout.addWidget(self._pixgrid_group)
        self._gridLayout.addWidget(self._selection_group)
        self._gridLayout.addWidget(self._buttonBox)

class CanvasDecorationsPopup(QMenu):
    def __init__(self, parent: QWidget | None = None):
        super(CanvasDecorationsPopup, self).__init__(parent)
        self.config = CanvasDecorationsConfig()
        self.config.load()
        self.reloadMenus()
    
    def refreshView(self):
        
        def slotConfigChanged(obj: QObject):
            canvas_call = getattr(obj, "slotConfigChanged", None)
            if callable(canvas_call):
                canvas_call()
        
        qwin = Krita.instance().activeWindow().qwindow()
        for i, view in enumerate(Krita.instance().activeWindow().views()):
            view_obj = qwin.findChild(QWidget,'view_' + str(i))     
            for child in view_obj.children():
                slotConfigChanged(child)
            
            canvas_obj = view_obj.findChild(QOpenGLWidget)
            slotConfigChanged(canvas_obj)
            
        for docker in Krita.instance().dockers():
            if (docker.objectName() == "KisLayerBox"):
                slotConfigChanged(docker)
    
    def reloadMenus(self):
        def createMenu(mode):
            menu = QMenu(self)            
            for index in self.config.canvas_presets:
                text = self.config.canvas_presets[index].presetName
                if mode == "remove":
                    connection = (lambda x=index: self.removePreset(x))
                elif mode == "edit":
                    connection = (lambda x=index: self.editPreset(x))
                menu.addAction(text, connection)
            return menu
        
        
        self.addSeparator().setText("Presets")
        
        for index in self.config.canvas_presets:
            text = self.config.canvas_presets[index].presetName
            connection = (lambda x=index: self.activatePreset(x))
            self.addAction(text, connection)

        self.addSeparator()
        
        self.addAction(Krita.instance().icon("list-add"), "New Preset", self.addPreset)
        
        editMenu = createMenu("edit")
        editMenu.setIcon(Krita.instance().icon("document-edit"))
        editMenu.setTitle("Edit Preset...")
        self.addMenu(editMenu)
        
        deleteMenu = createMenu("remove")
        deleteMenu.setIcon(Krita.instance().icon("edit-delete"))
        deleteMenu.setTitle("Delete Preset...")
        self.addMenu(deleteMenu)
                
    def addPreset(self):
        dlg = CanvasDecorationsEditor(CanvasDecorationsPreset.current(), self)
        if dlg.exec_():
            self.config.canvas_presets[str("new")] = dlg.preset
            self.config.save()
            
    def editPreset(self, index: int):
        dlg = CanvasDecorationsEditor(self.config.canvas_presets[index], self)
        if dlg.exec_():
            self.config.canvas_presets[index] = dlg.preset
            self.config.save()
    
    def removePreset(self, index: int):
        self.config.canvas_presets.pop(index)
        self.config.save()
        
    def activatePreset(self, index: int):
        self.config.canvas_presets[index].activate()
        self.refreshView()
                   
    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def onCanvasChanged(self, canvas: Canvas):
        active_window = Krita.instance().activeWindow()
        if active_window == None: return

        active_view = active_window.activeView()
        if active_view == None: return