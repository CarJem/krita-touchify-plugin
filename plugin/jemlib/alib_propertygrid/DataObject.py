class DataObject:
    def propertygrid_labels(self):
        return []
    
    def propertygrid_hints(self):
        return {}
    
    def propertygrid_hidden(self):
        return {}
    
    def propertygrid_sisters(self):
        return {}
    
    def propertygrid_sorted(self):
        return []
    
    def propertygrid_restrictions(self) -> list[dict[str, any]]:
        return []
    
    def propertygrid_view_type(self):
        return "default"
    
    def propertygrid_on_duplicate(self):
        pass

    def propertygrid_icon(self):
        return None
    
    def propertygrid_listload(self):
        pass
    
    def propertygrid_listmod(self):
        pass