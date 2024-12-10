
class Extensions:
    def tryPraseFloat(s: str, defaultValue: float):
        try:
            i = float(s)
            return i
        except ValueError as verr:
            return defaultValue
        except Exception as ex:
            return defaultValue
    
    def tryPraseInt(s: str, defaultValue: int):
        try:
            i = int(s)
            return i
        except ValueError as verr:
            return defaultValue
        except Exception as ex:
            return defaultValue
    
    def extend(class_to_extend):
        def decorator(extending_class):
            class_to_extend.__dict__.update(extending_class.__dict__)
            return class_to_extend
        return decorator
    

    

