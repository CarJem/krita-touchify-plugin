from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *

from touchify.__env__ import *
from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.managers.shared.events import GlobalEvents

from touchify.src.PluginWindow import TouchifyWindow

class TouchifyPlugin(Extension):

    class WorkerTasks(QObject):
        @staticmethod
        def OnWindowCreated(self: "TouchifyPlugin"):
            # Thread
            self.worker_thread = QThread()
            # Worker
            self.worker_instance = TouchifyPlugin.WorkerTasks()
            self.worker_instance.moveToThread( self.worker_thread )
            # Thread
            self.worker_thread.started.connect( lambda : self.worker_instance.OnWindowCreatedAsync( self ) )
            self.worker_thread.start()

        def OnWindowCreatedAsync(a, self: "TouchifyPlugin"):
            window: WindowAPI | None = None
            window_id = self.new_instance.Window_UUID()

            for __window in KritaAPI.get_windows():
                if __window.qwindow().property("KRITA_TOUCHIFY_IS_LOADED") != True:
                    __window.qwindow().setProperty("KRITA_TOUCHIFY_IS_LOADED", True)
                    window = __window
            
            if window == None: return

            window.windowClosed.connect(lambda: self.onWindowDestroyed(window_id))
            self.instances[window_id] = self.new_instance
            self.instances[window_id].Window_Load(window)

            self.setup_instance = False
    

    instances: dict[str, TouchifyWindow] = {}
    setup_instance: bool = False
    new_instance: TouchifyWindow = None

    def __init__(self, parent):
        super().__init__(parent)
        self.event_handler = GlobalEvents(self)
        self.DEV_HOOK_FIND_PLUGIN = "TOUCHIFY"

    def setup(self):
        KritaAPI.notifier().add_window_created_callback(self.onWindowCreated)
        KritaAPI.notifier().add_configuration_changed_callback(self.onConfigurationChanged)


        self.intervalTimer = QTimer(self)
        self.intervalTimer.timeout.connect(GlobalEvents.EMIT_SIGNAL_TIMER_TICKED)
        self.intervalTimer.start(250)
    
    def onWindowDestroyed(self, windowId: str):
        item: TouchifyWindow = self.instances[windowId]
        item.Window_Unload()
        item.deleteLater()
        del self.instances[windowId]

    def onWindowCreated(self):
        if not self.setup_instance: return
        TouchifyPlugin.WorkerTasks.OnWindowCreated(self)

    def onConfigurationChanged(self):
        GlobalEvents.EMIT_SIGNAL_KRITA_CONFIG_UPDATED()

    def createActions(self, window: Window):
        self.setup_instance = True
        self.new_instance = TouchifyWindow(self)
        self.new_instance.Actions_Init(WindowAPI(window))



