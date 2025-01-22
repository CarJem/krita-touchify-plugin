import copy
from dataclasses import dataclass
import json
from typing import Optional

@dataclass
class SessionRef:
    path: str
    path_type: str

@dataclass
class SessionGrid:
    path: str
    path_type: str
    filter: str

@dataclass
class SessionPreview:
    path: str
    path_type: str

@dataclass
class SessionTab:
    name: str
    preview: SessionPreview
    grid: SessionGrid
    ref: SessionRef
    active_mode: Optional[str]

    @classmethod
    def from_dict(cls, item: dict):
        result = copy.deepcopy(item)

        if isinstance(item["preview"], dict):
            result["preview"] = item['preview'] = SessionPreview(**item['preview'])
        else:
            result["preview"] = None

        if isinstance(item["grid"], dict):
            result["grid"] = item['grid'] = SessionGrid(**item['grid'])
        else:
            result["grid"] = None

        if isinstance(item["ref"], dict):
            result["ref"] = item['ref'] = SessionRef(**item['ref'])
        else:
            result["ref"] = None

        return cls(**result)

@dataclass
class Session:
    tabs: list[SessionTab]
    active_tab: Optional[int]

    @classmethod
    def read(cls, string: str):
        data: dict = json.loads(string)

        if isinstance(data["tabs"], list):
            dict_list: list = data["tabs"]
            actual_list: list[SessionTab] = []
            for item in dict_list:
                if not isinstance(item, dict): continue
                tab = SessionTab.from_dict(item)
                actual_list.append(tab)
            data["tabs"] = actual_list

        return cls(**data)

    def write(self):
        return json.dumps(self, default=lambda o: o.__dict__)