from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from typing import TYPE_CHECKING

from touchify.src.cfg.widget_layout.WidgetLayoutPadOptions import WidgetLayoutPadOptions
from touchify.src.cfg.widget_layout.WidgetLayoutToolboxOptions import WidgetLayoutToolboxOptions
from touchify.src.components.krita.settings import KritaSettings
from touchify.src.components.touchify.canvas.NtToolbox import NtToolbox
from touchify.src.components.touchify.canvas.NtToolshelf import NtToolshelf
from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from touchify.src.variables import TOUCHIFY_ID_SETTINGS_WIDGETPAD

if TYPE_CHECKING:
    from touchify.src.components.touchify.canvas.NtCanvas import NtCanvas

class NtWorker(QObject):

    def run( self: "NtWorker", canvas: "NtCanvas", mode: str, args: dict ):
        if mode == "LOAD_ELEMENTS": self.PROCESS_ELEMENTS(canvas)
        elif mode == "RELOAD_ELEMENTS": self.PROCESS_ELEMENTS(canvas, True)
        elif mode == "ACTIONS":  self.PROCESS_ACTIONS(canvas, str(args.get("pad")), bool(args.get("value")) )
        elif mode == "VIEW": self.PROCESS_VIEW(canvas)

        if canvas.thread_packer: 
            canvas.thread_packer.quit()
            canvas.clearMask()

    def PROCESS_ELEMENTS (self: "NtWorker", canvas: "NtCanvas", full_unload: bool = False ):
        def onToolshelfCheck(toolshelf: NtToolshelf | None, allow_toolshelf: bool, config_index: int, action: QAction):
            if toolshelf == None and allow_toolshelf:
                actual_toolshelf = NtToolshelf(canvas, canvas.Window(), config_index, canvas.app_engine)
                actual_toolshelf.SIGNAL_RESIZED.connect(canvas.widgetResizeEvent)
                actual_toolshelf.collapseBtn.setDefaultAction(action)
                canvas.canvasLayout.addWidget(actual_toolshelf)
                actual_toolshelf.show()
                return actual_toolshelf
            elif toolshelf and not allow_toolshelf:
                toolshelf.SIGNAL_RESIZED.disconnect(canvas.widgetResizeEvent)
                toolshelf.close()
                canvas.canvasLayout.removeWidget(toolshelf)
                return None
            else:
                return "ignore"
        
        def onToolboxCheck(allow_toolbox: bool):
            if canvas.toolbox == None and allow_toolbox:
                canvas.toolbox = NtToolbox(canvas, canvas.Window())
                canvas.toolbox.SIGNAL_RESIZED.connect(canvas.widgetResizeEvent)
                canvas.toolbox.collapseBtn.setDefaultAction(canvas.tlb_action)
                canvas.canvasLayout.addWidget(canvas.toolbox)
                canvas.toolbox.show()
            elif canvas.toolbox and not allow_toolbox:
                canvas.canvasLayout.removeWidget(canvas.toolbox)
                canvas.toolbox.SIGNAL_RESIZED.connect(canvas.widgetResizeEvent)
                canvas.toolbox.close()
                canvas.toolbox = None

        def insertWidgetPad(pad: NtWidgetPad, padOptions: WidgetLayoutPadOptions | WidgetLayoutToolboxOptions):
            alignment_x = WidgetLayoutPadOptions.HorizontalAlignment.toAlignmentFlag(padOptions.alignment_x)
            alignment_y = WidgetLayoutPadOptions.VerticalAlignment.toAlignmentFlag(padOptions.alignment_y)
            pad.setCanvasData(alignment_x, alignment_y)

            if padOptions.span_x != -1 and padOptions.span_y != -1:
                canvas.canvasLayout.addWidget(pad, padOptions.position_y, padOptions.position_x, padOptions.span_y, padOptions.span_x, alignment_x | alignment_y)
            else:
                canvas.canvasLayout.addWidget(pad, padOptions.position_y, padOptions.position_x, alignment_x | alignment_y)
            canvas.canvasLayout.setColumnStretch(padOptions.position_x, padOptions.stretch_x)
            canvas.canvasLayout.setRowStretch(padOptions.position_y, padOptions.stretch_y)
        
        #print(f"NtCanvas | updateElements | start | {QTime.currentTime().toString()}")

        if full_unload:
            onToolboxCheck(False)

            alpha = onToolshelfCheck(canvas.toolshelf_alpha, False, 0, canvas.tlshlf_alpha_action)
            if alpha != "ignore": canvas.toolshelf_alpha = alpha

            beta = onToolshelfCheck(canvas.toolshelf_beta,  False, 1, canvas.tlshlf_beta_action)
            if beta != "ignore": canvas.toolshelf_beta = beta

            gamma = onToolshelfCheck(canvas.toolshelf_gamma, False, 2, canvas.tlshlf_gamma_action)
            if gamma != "ignore": canvas.toolshelf_gamma = gamma

            delta = onToolshelfCheck(canvas.toolshelf_delta, False, 3, canvas.tlshlf_delta_action)
            if delta != "ignore": canvas.toolshelf_delta = delta

        #print(f"NtCanvas | updateElements | post_unload | {QTime.currentTime().toString()}")
        
        
        allow_toolbox = canvas.toolbox_enabled
        allow_toolshelf_alpha = canvas.toolshelf_count >= 1
        allow_toolshelf_beta = canvas.toolshelf_count >= 2
        allow_toolshelf_gamma = canvas.toolshelf_count >= 3
        allow_toolshelf_delta = canvas.toolshelf_count >= 4

        onToolboxCheck(allow_toolbox)

        alpha = onToolshelfCheck(canvas.toolshelf_alpha, allow_toolshelf_alpha, 0, canvas.tlshlf_alpha_action)
        if alpha != "ignore": canvas.toolshelf_alpha = alpha

        beta = onToolshelfCheck(canvas.toolshelf_beta,  allow_toolshelf_beta, 1, canvas.tlshlf_beta_action)
        if beta != "ignore": canvas.toolshelf_beta = beta

        gamma = onToolshelfCheck(canvas.toolshelf_gamma, allow_toolshelf_gamma, 2, canvas.tlshlf_gamma_action)
        if gamma != "ignore": canvas.toolshelf_gamma = gamma

        delta = onToolshelfCheck(canvas.toolshelf_delta, allow_toolshelf_delta, 3, canvas.tlshlf_delta_action)
        if delta != "ignore": canvas.toolshelf_delta = delta

        #print(f"NtCanvas | updateElements | post_check | {QTime.currentTime().toString()}")

        for x in range(canvas.canvasLayout.columnCount()):
            canvas.canvasLayout.setColumnStretch(x, 0)

        for y in range(canvas.canvasLayout.rowCount()):
            canvas.canvasLayout.setRowStretch(y, 0)

        #print(f"NtCanvas | updateElements | post_reset_stretch | {QTime.currentTime().toString()}")

        if canvas.toolbox: insertWidgetPad(canvas.toolbox, canvas.active_preset.toolbox)
        if canvas.toolshelf_alpha: insertWidgetPad(canvas.toolshelf_alpha, canvas.active_preset.toolshelf_alpha)
        if canvas.toolshelf_beta: insertWidgetPad(canvas.toolshelf_beta, canvas.active_preset.toolshelf_beta)
        if canvas.toolshelf_gamma: insertWidgetPad(canvas.toolshelf_gamma, canvas.active_preset.toolshelf_gamma)
        if canvas.toolshelf_delta: insertWidgetPad(canvas.toolshelf_delta, canvas.active_preset.toolshelf_delta)

        #print(f"NtCanvas | updateElements | post_insert | {QTime.currentTime().toString()}")

        self.PROCESS_ACTIONS(canvas)

        #print(f"NtCanvas | updateElements | end | {QTime.currentTime().toString()}")

    def PROCESS_ACTIONS(self: "NtWorker", canvas: "NtCanvas", pad: str = "", value: bool = None):
        if canvas.State_WindowLoaded() == False:
            return
        

        show_toolbox = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolbox"), True)
        show_toolshelf_alpha = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_alpha"), True)
        show_toolshelf_beta = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_beta"), True)
        show_toolshelf_gamma = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_gamma"), True)
        show_toolshelf_delta = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_delta"), True)
        
        if pad != "" and value != None:
            KritaSettings.writeSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format(pad), value, False)
            match pad:
                case "toolbox": show_toolbox = value
                case "toolshelf_alpha": show_toolshelf_alpha = value
                case "toolshelf_beta":  show_toolshelf_beta = value
                case "toolshelf_gamma": show_toolshelf_gamma = value
                case "toolshelf_delta": show_toolshelf_delta = value
                case _: pass


        canvas.tlb_action.setChecked(show_toolbox)
        canvas.tlshlf_alpha_action.setChecked(show_toolshelf_alpha)
        canvas.tlshlf_beta_action.setChecked(show_toolshelf_beta)
        canvas.tlshlf_gamma_action.setChecked(show_toolshelf_gamma)
        canvas.tlshlf_delta_action.setChecked(show_toolshelf_delta)
    
        if canvas.toolbox: canvas.toolbox.setCollapsed(show_toolbox)
        if canvas.toolshelf_alpha: canvas.toolshelf_alpha.setCollapsed(show_toolshelf_alpha)
        if canvas.toolshelf_beta:  canvas.toolshelf_beta.setCollapsed(show_toolshelf_beta)
        if canvas.toolshelf_gamma: canvas.toolshelf_gamma.setCollapsed(show_toolshelf_gamma)
        if canvas.toolshelf_delta: canvas.toolshelf_delta.setCollapsed(show_toolshelf_delta)

        self.PROCESS_VIEW(canvas)

    def PROCESS_VIEW(self: "NtWorker", canvas: "NtCanvas",):
        if canvas.State_WindowLoaded() == False:
            return

        def rulerMargin():
            padding = 4
            # Canvas ruler pixel width on Windows
            if KritaSettings.showRulers(): return 20 + padding
            return 0

        def scrollBarMargin():
            padding = 4
            # Canvas scrollbar pixel width/height on Windows 
            if KritaSettings.hideScrollbars(): return 0
            return 10 + padding

        if canvas.MdiArea():
            position = canvas.MdiArea().viewport().pos()
            size = canvas.MdiArea().viewport().size()

            position.setX(position.x() + rulerMargin())
            position.setY(position.y() + rulerMargin())

            size.setWidth(size.width() - rulerMargin() - scrollBarMargin())
            size.setHeight(size.height() - rulerMargin() - scrollBarMargin())

            if canvas.State_IsEmpty():
                canvas.move(position)
                canvas.setFixedSize(0, 0)
            else:
                canvas.move(position)
                canvas.setFixedSize(size)
    
            if canvas.toolbox: canvas.toolbox.adjustToView()
            if canvas.toolshelf_alpha: canvas.toolshelf_alpha.adjustToView()
            if canvas.toolshelf_beta: canvas.toolshelf_beta.adjustToView()
            if canvas.toolshelf_gamma: canvas.toolshelf_gamma.adjustToView()
            if canvas.toolshelf_delta: canvas.toolshelf_delta.adjustToView()