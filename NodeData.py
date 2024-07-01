# NodeData.py

from dataclasses import dataclass, asdict, field
from typing import List

@dataclass
class Serializable:
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class NodeData(Serializable):
    
    # "START", "AGENT", "TASK", "STEP", "TEAM"
    type: str = ""

    uniq_id: str = ""
    pos_x: float = 0.0
    pos_y: float = 0.0
    width: float = 200.0  # Default width
    height: float = 200.0  # Default height

    # AGENT
    name: str = ""
    description: str = ""

    # TASK
    team: str = ""

    # STEP
    agent: str = ""
    tool: str = ""
    task: str = ""
    output_var: str = ""

    # Tool
    description: str = ""


    nexts: List[int] = field(default_factory=list)
    prevs: List[int] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
