from enum import Enum


class DockerPosition(Enum):
    DockTornOff = 0
    DockTop = 1
    DockBottom = 2
    DockRight = 3
    DockLeft = 4
    DockMinimized = 5