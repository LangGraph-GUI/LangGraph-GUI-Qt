# NodeData.py

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict

@dataclass
class Serializable:
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class NodeData(Serializable):
    
    # Graph Feature
    uniq_id: str = ""
    
    # Store external properties in a dictionary
    ext: dict = field(default_factory=dict)


    nexts: List[int] = field(default_factory=list)

    # LangGraph attribute
    # "START", "STEP", "TOOL", "CONDITION"
    type: str = "START"

    # AGENT
    name: str = ""
    description: str = ""

    # STEP
    tool: str = ""

    # CONDITION
    true_next: Optional[int] = None
    false_next: Optional[int] = None


    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
