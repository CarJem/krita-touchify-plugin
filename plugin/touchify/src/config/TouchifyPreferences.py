from jemlib.api_touchify.env import TouchifyEnv
from jemlib.managers.KritaSettings import KritaSettings
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class TouchifyPreferences:

    class Tweaks:
        def __init__(self):
            self.borderless_toolbar = False
            self.thin_document_tabs = False
            self.enable_privacy_mode = False
            self.docked_brush_editor = False
            self.brush_editor_zoomfix = False

        def load(self):
            self.borderless_toolbar = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "borderless_toolbar", False)
            self.thin_document_tabs = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "thin_document_tabs", False)
            self.enable_privacy_mode = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "enable_privacy_mode", False)
            self.docked_brush_editor = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "docked_brush_editor", False)
            self.brush_editor_zoomfix = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "brush_editor_zoomfix", False)

        def save(self):
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "borderless_toolbar", self.borderless_toolbar, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "thin_document_tabs", self.thin_document_tabs, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "enable_privacy_mode", self.enable_privacy_mode, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "docked_brush_editor", self.docked_brush_editor, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_TWEAKS, "brush_editor_zoomfix", self.brush_editor_zoomfix, False)

        def propertygrid_view_type(self):
            return "form"

        def propertygrid_hidden(self):
            result = []
            return result
        
        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["style_options"] = { 
                "items": [
                    "borderless_toolbar", 
                    "thin_document_tabs"
                ], 
                "use_labels": True, 
                "flip_labels": False
            }
            row["brush_editor_options"] = { 
                "items": [
                    "docked_brush_editor", 
                    "brush_editor_zoomfix"
                ], 
                "use_labels": True, 
                "flip_labels": False
            }
            row["other_options"] = { 
                "items": [
                    "enable_privacy_mode"
                ], 
                "use_labels": True, 
                "flip_labels": False
            }

            return row

        def propertygrid_labels(self):
            return {
                "style_options": "Style Options",
                "borderless_toolbar": "Use Borderless Toolbars",
                "thin_document_tabs": "Use Thin Document Tabs",

                "brush_editor_options": "Brush Editor Options",
                "docked_brush_editor": "Enable Docked Mode",
                "brush_editor_zoomfix": "Enable ZoomFix Workaround",

                "other_options": "Other Options",
                "enable_privacy_mode": "Enable Privacy Mode",
            }

    class Dockers:
        def __init__(self):
            self.hidden_dockers_left: str = ""
            self.hidden_dockers_right: str = ""
            self.hidden_dockers_up: str = ""
            self.hidden_dockers_down: str = ""

            self.number_of_widgetpads: int = 4
            self.number_of_toolshelves: int = 4
        
        def load(self):
            self.hidden_dockers_left = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_left", "")
            self.hidden_dockers_right = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_right", "")
            self.hidden_dockers_up = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_up", "")
            self.hidden_dockers_down = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_down", "")

            self.number_of_widgetpads = KritaSettings.readSettingInt(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "number_of_widgetpads", 4)
            self.number_of_toolshelves = KritaSettings.readSettingInt(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "number_of_toolshelves", 4)

        def save(self):
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_left", self.hidden_dockers_left, False)
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_right", self.hidden_dockers_right, False)
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_up", self.hidden_dockers_up, False)
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "hidden_dockers_down", self.hidden_dockers_down, False)

            KritaSettings.writeSettingInt(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "number_of_widgetpads", self.number_of_widgetpads, False)
            KritaSettings.writeSettingInt(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_DOCKERS, "number_of_toolshelves", self.number_of_toolshelves, False)

        def propertygrid_view_type(self):
            return "form"
        
        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["toolshelf_options"] = { 
                "items": [
                    "number_of_widgetpads", 
                    "number_of_toolshelves"
                ], 
                "use_labels": True, 
                "flip_labels": True
            }

            return row
        
        def propertygrid_labels(self):
            return {
                "toolshelf_options": "Toolshelf / WidgetPad Settings",
                "number_of_widgetpads": "Number of WidgetPads",
                "number_of_toolshelves": "Number of Toolshelves",
            }

        def propertygrid_hidden(self):
            return [
                "hidden_dockers_left",
                "hidden_dockers_right",
                "hidden_dockers_up",
                "hidden_dockers_down"
            ]

        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["number_of_widgetpads"] = DataConstraints.range(1, 10)
            restrictions["number_of_toolshelves"] = DataConstraints.range(1, 10)
            return restrictions

    class Canvas:
        def __init__(self):
            self.canvas_right_click_action: str = ""
            self.canvas_left_click_action: str = ""
            self.canvas_middle_click_action: str = ""
        
        def load(self):
            self.canvas_right_click_action = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_CANVAS, "canvas_right_click_action", "")
            self.canvas_left_click_action = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_CANVAS, "canvas_left_click_action", "")
            self.canvas_middle_click_action = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_CANVAS, "canvas_middle_click_action", "")

        def save(self):
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_CANVAS, "canvas_right_click_action", self.canvas_right_click_action, False)
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_CANVAS, "canvas_left_click_action", self.canvas_left_click_action, False)
            KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_CANVAS, "canvas_middle_click_action", self.canvas_middle_click_action, False)

        def propertygrid_view_type(self):
            return "form"

        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["canvas_right_click_action"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
            restrictions["canvas_left_click_action"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
            restrictions["canvas_middle_click_action"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
            return restrictions
        
        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["click_overrides"] = { 
                "items": [
                    "canvas_right_click_action", 
                    "canvas_left_click_action",
                    "canvas_middle_click_action"
                ], 
                "use_labels": True, 
                "flip_labels": True
            }

            return row
    
        def propertygrid_labels(self):
            return {
                "click_overrides": "Input Overrides",
                "canvas_right_click_action": "Right Click",
                "canvas_left_click_action": "Left Click",
                "canvas_middle_click_action": "Middle Click",
            }
    
    class Brushes:
        def __init__(self):
            self.preset_specific_options: bool = False
        
        def load(self):
            self.preset_specific_options = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_BRUSHES, "preset_specific_options", False)

        def save(self):
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_BRUSHES, "preset_specific_options", self.preset_specific_options, False)

        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["tool_options"] = { 
                "items": [
                    "preset_specific_options"
                ], 
                "use_labels": True, 
                "flip_labels": False
            }

            return row

        def propertygrid_view_type(self):
            return "form"
        
        def propertygrid_labels(self):
            return {
                "tool_options": "Tool Options",
                "preset_specific_options": "Preset-Specific Options",
            }

    class Application:
        def __init__(self):
            self.Application_EnableMenuIcons: bool = False
            self.Application_EnableScalingWorkarounds: bool = False
            
            self.Scaling_UseFakeHighDpiScaling: bool = False
            self.Scaling_UseHighDpiPixmaps: bool = False
            self.Scaling_Use96Dpi: bool = False
            self.Scaling_UseAdjustedFontScale: bool = False
            self.Scaling_AdjustedFontScale: float = 0.0
        
        def load(self):
            self.Application_EnableMenuIcons = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Application_EnableMenuIcons", False)
            self.Application_EnableScalingWorkarounds = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Application_EnableScalingWorkarounds", False)

            self.Scaling_UseFakeHighDpiScaling = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_UseFakeHighDpiScaling", False)
            self.Scaling_UseHighDpiPixmaps = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_UseHighDpiPixmaps", False)
            self.Scaling_Use96Dpi = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_Use96Dpi", False)
            self.Scaling_UseAdjustedFontScale = KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_UseAdjustedFontScale", False)
            self.Scaling_AdjustedFontScale = KritaSettings.readSettingFloat(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_AdjustedFontScale", 0.0)

        def save(self):
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Application_EnableMenuIcons", self.Application_EnableMenuIcons, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Application_EnableScalingWorkarounds", self.Application_EnableScalingWorkarounds, False)

            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_UseFakeHighDpiScaling", self.Scaling_UseFakeHighDpiScaling, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_Use96Dpi", self.Scaling_Use96Dpi, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_UseHighDpiPixmaps", self.Scaling_UseHighDpiPixmaps, False)
            KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_UseAdjustedFontScale", self.Scaling_UseAdjustedFontScale, False)
            KritaSettings.writeSettingFloat(TouchifyEnv.SettingsPath.TOUCHIFY_CONFIG_APPLICATION, "Scaling_AdjustedFontScale", self.Scaling_AdjustedFontScale, False)
        
        def propertygrid_view_type(self):
            return "form"

        def propertygrid_labels(self):
            return {
                "application_overrides": "Application Overrides",
                "Application_EnableMenuIcons": "Enable Menu Icons",
                "Application_EnableScalingWorkarounds": "Enable Scaling Workarounds",
                "Scaling_UseFakeHighDpiScaling": "Enable Fake High Dpi Scaling", 
                "Scaling_UseHighDpiPixmaps": "Enable High Dpi Pixmaps",
                "Scaling_Use96Dpi": "Enable 96Dpi Mode",
                "Scaling_UseAdjustedFontScale": "Adjust Font Scale",
                "Scaling_AdjustedFontScale": ""
            }

        def propertygrid_hidden(self):
            result = []

            if not self.Application_EnableScalingWorkarounds:
                result.append("Scaling_UseFakeHighDpiScaling")
                result.append("Scaling_UseHighDpiPixmaps")
                result.append("Scaling_Use96Dpi")
                result.append("Scaling_UseAdjustedFontScale")

            if not self.Application_EnableScalingWorkarounds or not self.Scaling_UseAdjustedFontScale:
                result.append("Scaling_AdjustedFontScale")
                

            return result

        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["application_overrides"] = { 
                "items": [
                    "Application_EnableMenuIcons",
                    "Application_EnableScalingWorkarounds", 

                    "Scaling_UseFakeHighDpiScaling", 
                    "Scaling_UseHighDpiPixmaps",
                    "Scaling_Use96Dpi",
                    "Scaling_UseAdjustedFontScale",
                    "Scaling_AdjustedFontScale",
                ], 
                "use_labels": True, 
                "flip_labels": False
            }

            return row

        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["Scaling_AdjustedFontScale"] = DataConstraints.range(-10, 10)
            return restrictions

    def __init__(self) -> None:
        self.tweaks = self.Tweaks()
        self.dockers = self.Dockers()
        self.canvas = self.Canvas()
        self.brushes = self.Brushes()
        self.application = self.Application()

    def load(self):
        self.tweaks.load()
        self.dockers.load()
        self.canvas.load()
        self.brushes.load()
        self.application.load()

    def save(self):
        self.tweaks.save()
        self.dockers.save()
        self.canvas.save()
        self.brushes.save()
        self.application.save()
    
    def propertygrid_view_type(self):
        return "tabs"
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        return row
    
    def propertygrid_hidden(self):
        result = []
        return result
    
    def propertygrid_sorted(self):
        return []
    
    def propertygrid_labels(self):
        return {
            "tweaks": "Tweaks",
            "brushes": "Brushes",
            "canvas": "Canvas",
            "dockers": "Dockers",
            "application": "Application"
        }

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["tweaks"] = DataConstraints.expandable()
        restrictions["brushes"] = DataConstraints.expandable()
        restrictions["canvas"] = DataConstraints.expandable()
        restrictions["dockers"] = DataConstraints.expandable()
        restrictions["application"] = DataConstraints.expandable()
        return restrictions