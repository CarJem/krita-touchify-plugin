import inspect

from .TypedList import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

from krita import *

def nameof(obj: any, namespace: dict[str, Any]):
    return [name for name in namespace if namespace[name] is obj]


class Extensions:
    def extend(class_to_extend):
        def decorator(extending_class):
            class_to_extend.__dict__.update(extending_class.__dict__)
            return class_to_extend
        return decorator
    

    

