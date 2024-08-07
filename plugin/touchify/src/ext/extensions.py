import inspect

from .TypedList import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

from krita import *

def nameof(var):
    current_frame = inspect.currentframe()
    try:
        frame_locals = current_frame.f_back.f_locals
        var_name = [name for name, value in frame_locals.items() if value is var][0]
        print(f"Variable name: {var_name}")
        return var_name
    finally:
        del current_frame


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
    

    

