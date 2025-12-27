from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class GraphSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"

@dataclass
class GraphTags:
    directed: Optional[bool] = None
    weighted: Optional[bool] = None
    connected: Optional[bool] = None
    mixed: Optional[bool] = None
    full: Optional[bool] = None
    double: Optional[bool] = None
    simple: Optional[bool] = None
    empty: Optional[bool] = None
    planar: Optional[bool] = None
    tree: Optional[bool] = None
    pseudo: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphTags':
        """Создает GraphTags из словаря свойств графа"""
        tags = cls()
        for key in data:
            if hasattr(tags, key):
                setattr(tags, key, data[key])
        return tags

@dataclass
class GraphRequest:
    author: Optional[str] = None
    size: Optional[GraphSize] = None
    tags: Optional[GraphTags] = None
    strict_search: bool = True

    def is_empty(self) -> bool:
        """Проверяет, пустой ли запрос (все параметры None)"""
        return (self.author is None and 
                self.size is None and 
                self.tags is None)