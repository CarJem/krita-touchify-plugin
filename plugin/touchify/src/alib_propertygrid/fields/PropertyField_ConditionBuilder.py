from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *


from jemlib.alib_propertygrid.PropertyGrid import *
from jemlib.alib_propertygrid.fields.PropertyField import *
from touchify.src.alib_propertygrid.dialogs.ConditionBuilderDialog import ConditionBuilderDialog

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler



class PropertyField_ConditionBuilder(PropertyField[str]):
    def __init__(self, handler: "DataHandler", property: DataPath[str]):
        super().__init__(handler, property, True)

        self.helper_dlg = None

        conditions = property.variableData().split(",")
        while "" in conditions: conditions.remove("")
        condition_count = len(conditions)

        self.__label = QLabel(self)
        self.__label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.__label.setText(f"{condition_count} rules")

        self.__button = QPushButton(self)
        self.__button.setMaximumSize(24, 24)
        #self.__button.setContentsMargins(0,0,0,0)
        self.__button.clicked.connect(self.onBuilderRequested)
        self.__button.setIcon(IconRepository.iconLoader("properties"))
        self.__button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.__editorLayout = QHBoxLayout(self)
        self.__editorLayout.setSpacing(0)
        self.__editorLayout.setContentsMargins(0,0,0,0)
        self.__editorLayout.addWidget(self.__label, 1)
        self.__editorLayout.addWidget(self.__button)
        self.setLayout(self.__editorLayout)

    def onBuilderChangesAccepted(self, result: str):
        self.getParentContainer().navigateBackwards()
        if not result: return

        conditions = result.split(",")
        while "" in conditions: conditions.remove("")
        condition_count = len(conditions)
        self.__label.setText(f"{condition_count} rules")

        super().setVariable(result)
        
    def onBuilderChangesRejected(self):
        self.getParentContainer().navigateBackwards()

    def onBuilderRequested(self):
        self.helper_dlg: ConditionBuilderDialog = ConditionBuilderDialog.Setup(self.helper_dlg, self, "condition_builder", {
            'container': self.getParentContainer()
        })
        self.helper_dlg.onAcceptFunction = self.onBuilderChangesAccepted
        self.helper_dlg.onRejectFunction = self.onBuilderChangesRejected
        self.helper_dlg.setCurrentConditions(self.propertyData.variableData())
        self.helper_dlg.loadList()
        self.helper_dlg.showAsWidget()


