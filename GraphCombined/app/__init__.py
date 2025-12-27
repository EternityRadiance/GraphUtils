"""
Graph Search System - Объединенное приложение
"""

__version__ = "2.0.0"
__author__ = "Graph Systems Team"
__description__ = "Объединенная система поиска и визуализации графов"

# Экспортируем основные классы для удобного импорта
from .GraphFrontend import GraphSearchApp
from .GraphVisualizerApp import GraphVisualizerApp, GraphCanvas
from .CombinedFrontend import CombinedGraphApp, run_combined_app
from .ConsoleWidget import ConsoleWidget, get_console, log_info, log_success, log_warning, log_error, log_system
from .GraphService import GraphService
from .DataTypes import GraphRequest, GraphTags, GraphSize
from .graph_models import Graph, GraphProperties
from .explorer import GraphExplorer
from .graph_drawer import GraphDrawer
from .config import CONFIG

__all__ = [
    'GraphSearchApp',
    'GraphVisualizerApp',
    'GraphCanvas',
    'CombinedGraphApp',
    'run_combined_app',
    'ConsoleWidget',
    'get_console',
    'log_info',
    'log_success',
    'log_warning',
    'log_error',
    'log_system',
    'GraphService',
    'GraphRequest',
    'GraphTags',
    'GraphSize',
    'Graph',
    'GraphProperties',
    'GraphExplorer',
    'GraphDrawer',
    'CONFIG'
]