import inspect

from .typedlist import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

from krita import *

class Extensions:

    def nameof(exp):
        frame = sys._getframe(1)
        i = frame.f_lasti
        code = frame.f_code
        index = code.co_code[i - 1] * 256 + code.co_code[i - 2]
        op = code.co_code[i - 3]
        if op == 124: # local var
            return code.co_varnames[index]
        elif op == 116: # global var
            return code.co_names[index]
        else: #argument is not an identifier, fallback on source code extraction
            fname = frame.f_code.co_filename
            line = frame.f_lineno
            try:
                with open(fname) as f:
                    line = f.read().split('\n')[line - 1]
            except IOError:
                pass
            else:
                start = line.find('nameof(') + 7
                end = line.find(')', start)
                return line[start:end]
    
    def extend(class_to_extend):
        def decorator(extending_class):
            class_to_extend.__dict__.update(extending_class.__dict__)
            return class_to_extend
        return decorator
    

    

