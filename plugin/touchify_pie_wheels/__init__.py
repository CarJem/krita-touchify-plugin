import sys
import os
from touchify.src.api_krita import KritaAPI

sys.path.append(directory := os.path.dirname(__file__))

def main():
    from .src.Plugin import TouchifyPieWheelsPlugin
    KritaAPI.add_extension(TouchifyPieWheelsPlugin)

main()
