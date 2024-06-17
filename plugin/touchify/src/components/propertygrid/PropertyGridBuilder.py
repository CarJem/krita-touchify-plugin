from .PropertyGridHost import PropertyGridHost
from .PropertyGrid import PropertyGrid

class PropertyGridBuilder:
    def build(parentStack):
        return PropertyGrid(parentStack)
    
    def buildHost():
        propertyGridHost = PropertyGridHost()
        propertyGrid = PropertyGridBuilder.build(propertyGridHost)
        propertyGridHost.init(propertyGrid)
        return propertyGridHost
    
    def updateHostDataObject(obj: PropertyGridHost, data: any):
        if isinstance(obj.propertyGrid, PropertyGrid):
            obj.propertyGrid.updateDataObject(data)


