from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class GraphProperties:
    """Все свойства графа из GraphTags"""
    directed: bool
    weighted: bool
    connected: bool
    mixed: bool
    full: bool
    double: bool
    simple: bool
    empty: bool
    planar: bool
    tree: bool
    pseudo: bool

    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> 'GraphProperties':
        """Создает объект из словаря (пропускает отсутствующие ключи)"""
        default_values = {
            'directed': False,
            'weighted': False,
            'connected': False,
            'mixed': False,
            'full': False,
            'double': False,
            'simple': False,
            'empty': False,
            'planar': False,
            'tree': False,
            'pseudo': False
        }

        # Объединение стандартных значений с переданными данными
        merged = {**default_values, **data}
        return cls(**merged)

    def to_dict(self) -> Dict[str, bool]:
        """Преобразует в словарь"""
        return asdict(self)

    def is_directed(self) -> bool:
        """Проверяет, является ли граф направленным"""
        return self.directed

    def is_weighted(self) -> bool:
        """Проверяет, является ли граф взвешенным"""
        return self.weighted


@dataclass
class Graph:
    """Полная структура графа с параметрами"""
    author: str
    properties: GraphProperties
    size: str
    vertices: int
    edges: int
    edges_list: List[Dict[str, Any]]

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'Graph':
        """Создание Graph из JSON словаря"""
        # Получение свойств из JSON
        props_dict = json_data.get('properties', {})
        properties = GraphProperties.from_dict(props_dict)

        return cls(
            author=json_data['author'],
            properties=properties,
            size=json_data['size'],
            vertices=json_data['vertices'],
            edges=json_data['edges'],
            edges_list=json_data['edges_list']
        )

    def get_active_properties(self) -> List[str]:
        """Возвращение списка активных (True) свойств"""
        active = []
        props_dict = asdict(self.properties)

        for prop_name, prop_value in props_dict.items():
            if prop_value is True:
                active.append(prop_name)

        return active