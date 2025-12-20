from typing import TypeVar, Generic

from jemlib.alib_propertygrid.data.DataUtils import DataUtils

T = TypeVar("T")


class DataPath(Generic[T]):
    

    def __init__(self, name: str, source: any):
        self.__variable_name: str = name
        self.__variable_data: T = getattr(source, name)
        self.__variable_source: any = source

    def variableName(self):
        return self.__variable_name
    
    def variableType(self):
        return type(self.__variable_data)
    
    def variableListType(self):
        return DataUtils.getListType(self.__variable_data)
    
    def variableData(self):
        '''Get the current variable data stored, may not be in sync with other data'''
        return self.__variable_data
    
    def variableSource(self):
        return self.__variable_source

    def currentData(self):
        '''Get the current variable data directly from the source'''
        return getattr(self.__variable_source, self.__variable_name)

    def updateData(self, data: T):
        '''Forcefully update the data directly to the source. Will update it's own data to stay in sync'''
        setattr(self.__variable_source, self.__variable_name, data)
        self.__variable_data = data
