from dataclasses import dataclass
from typing import Optional

@dataclass
class ImageClip:
    state: bool
    cl: int
    ct: int
    cw: int
    ch: int

@dataclass
class InsertablePin:
    bx: int
    by: int
    image_path: Optional[str] = None