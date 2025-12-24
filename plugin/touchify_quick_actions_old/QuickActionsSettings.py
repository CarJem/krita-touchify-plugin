
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from jemlib.api_touchify.env import TouchifyEnv
from jemlib.managers.KritaSettings import KritaSettings

from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify.src.config.triggers.Trigger import Trigger



class QuickActionsSettings:

    def __init__(self, **args) -> None:
        self.actions: list[Trigger] = []
        JsonExtensions.dictToObject(self, args)
        self.actions = JsonExtensions.init_list(args, "actions", Trigger)

    def forceLoad(self):
        self.tabs = TypedList(self.actions, Trigger)

class QuickActionsSettingsLoader(QObject):

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._settings_cache: QuickActionsSettings = QuickActionsSettings()
        self.load()

    #region Saving / Loading

    def load(self):
        self._settings_cache = JsonExtensions.loadClass(KritaSettings.readSetting(TouchifyEnv.SettingsPath.QUICK_ACTIONS, "json", ""), QuickActionsSettings)
        self._settings_cache.forceLoad()

    def save(self):
        jsonData = JsonExtensions.saveClass(self._settings_cache)
        KritaSettings.writeSetting(TouchifyEnv.SettingsPath.QUICK_ACTIONS, "json", jsonData, False)

    #endregion

    def createActionTrigger(self, action_id: str):
        new_trigger = Trigger()
        new_trigger.variant = Trigger.Variants.Action
        new_trigger.action_id = action_id
        return new_trigger


    def actions(self):
        return self._settings_cache.actions