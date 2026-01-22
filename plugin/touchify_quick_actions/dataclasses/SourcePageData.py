from dataclasses import dataclass



@dataclass
class SourcePageData:
    name: str
    icon: str
    index: int
    active: bool