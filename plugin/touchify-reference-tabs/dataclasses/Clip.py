from dataclasses import dataclass


@dataclass
class Clip:
    state: bool
    cl: int
    ct: int
    cw: int
    ch: int