from dataclasses import dataclass
from typing import Optional


@dataclass
class InsertInfo:
    bx: int
    by: int
    image_path: Optional[str] = None