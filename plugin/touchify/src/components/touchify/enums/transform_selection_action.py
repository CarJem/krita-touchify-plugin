from enum import Enum


class TransformSelectionAction(Enum):
    Free_FlipX = 0
    Free_FlipY = 1
    Free_RotateCW = 2
    Free_RotateCCW = 3
    Apply = 4
    Reset = 5