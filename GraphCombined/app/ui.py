"""
Конфигурация пользовательского интерфейса для объединенного приложения
"""

from dataclasses import dataclass


@dataclass
class UIColorScheme:
    """Цветовая схема объединенного приложения"""
    # Основные цвета
    BACKGROUND = "#F8F4FF"
    PRIMARY = "#5D3FD3"
    SECONDARY = "#9370DB"
    ACCENT = "#90EE90"
    WARNING = "#FFD700"
    ERROR = "#FF6B6B"
    
    # Цвета фреймов
    AUTHOR_FRAME = "#E6E6FA"
    SIZE_FRAME = "#F0E6FF"
    TAGS_FRAME = "#F5F0FF"
    RESULTS_FRAME = "#F8F0FF"
    
    # Цвета строк таблицы
    EVEN_ROW = "#F5F0FF"
    ODD_ROW = "#FFF0F5"
    SELECTED_ROW = "#E6E6FA"
    STATUS_BAR = "#E6E6FA"
    
    # Градиенты для анимаций
    SUCCESS_GRADIENT = "#98FB98"  # светло-зелёный
    ERROR_GRADIENT = "#FFA07A"    # светло-коралловый
    
    # Цвета для визуализатора
    VISUALIZER_BG = "#F5F0FF"
    VISUALIZER_PANEL = "#FFFFFF"
    VISUALIZER_CANVAS = "#FFFFFF"
    VISUALIZER_ACCENT = "#D8BFD8"
    VISUALIZER_ACCENT_DARK = "#B19CD9"
    VISUALIZER_TEXT = "#333333"
    VISUALIZER_TEXT_LIGHT = "#666666"
    VISUALIZER_BORDER = "#E6E6FA"
    VISUALIZER_BUTTON_BG = "#D8BFD8"
    VISUALIZER_BUTTON_FG = "#333333"
    VISUALIZER_BUTTON_HOVER = "#B19CD9"
    VISUALIZER_VERTEX_NORMAL = "#D8BFD8"
    VISUALIZER_VERTEX_SELECTED = "#FFD700"
    VISUALIZER_EDGE_NORMAL = "#9370DB"
    VISUALIZER_EDGE_SELECTED = "#FFD700"
    VISUALIZER_ANIMATION_PULSE = "#FF6B9D"
    VISUALIZER_GLOW_EFFECT = "#FFFACD"
    
    # Цвета для Notebook (вкладок)
    NOTEBOOK_BG = "#F8F4FF"
    NOTEBOOK_TAB_BG = "#F8F4FF"
    NOTEBOOK_TAB_FG = "#000000"  # ЧЕРНЫЙ текст по умолчанию
    NOTEBOOK_TAB_SELECTED_BG = "#9370DB"
    NOTEBOOK_TAB_SELECTED_FG = "#FFFFFF"  # БЕЛЫЙ текст при выборе
    NOTEBOOK_TAB_ACTIVE_BG = "#E6E6FA"
    NOTEBOOK_TAB_BORDER = "#D8BFD8"


@dataclass
class UIFontScheme:
    """Шрифтовая схема приложения"""
    TITLE = ("Arial", 14, "bold")
    HEADER = ("Arial", 11, "bold")
    LABEL = ("Arial", 10)
    BUTTON = ("Arial", 10, "bold")
    ENTRY = ("Arial", 10)
    TREEVIEW = ("Arial", 10)
    TREEVIEW_HEADER = ("Arial", 10, "bold")
    
    # Шрифты для визуализатора
    VISUALIZER_TITLE = ("Arial", 12, "bold")
    VISUALIZER_BUTTON = ("Arial", 11, "bold")
    VISUALIZER_INFO = ("Arial", 9)
    VISUALIZER_VERTEX = ("Arial", 12, "bold")
    
    # Шрифты для Notebook
    NOTEBOOK_TAB = ("Arial", 10, "bold")


@dataclass
class UISizeScheme:
    """Размерная схема приложения"""
    # Основные размеры
    WINDOW = "1400x850"
    RESULTS_TREE_HEIGHT = 22
    AUTHOR_ENTRY_WIDTH = 30
    BUTTON_WIDTH_NORMAL = 22
    BUTTON_WIDTH_LARGE = 20
    
    # Минимальные размеры окон
    MIN_WINDOW_WIDTH = 1200
    MIN_WINDOW_HEIGHT = 700
    
    # Размеры для визуализатора
    VISUALIZER_WINDOW = "1600x900"
    VISUALIZER_CANVAS_WIDTH = 1200
    VISUALIZER_CANVAS_HEIGHT = 700
    VISUALIZER_PANEL_WIDTH = 350
    VISUALIZER_BUTTON_WIDTH = 220
    VISUALIZER_BUTTON_HEIGHT = 45
    
    # Размеры для Notebook
    NOTEBOOK_TAB_PADDING_H = 15  # Горизонтальный отступ
    NOTEBOOK_TAB_PADDING_V = 8   # Вертикальный отступ
    
    # Анимации
    GRADIENT_STEPS = 12
    GRADIENT_SPEED = 40  # ms


@dataclass
class UIPaddingScheme:
    """Схема отступов"""
    SMALL = "5"
    MEDIUM = "10"
    LARGE = "15"
    
    # Отступы для визуализатора
    VISUALIZER_SMALL = "5"
    VISUALIZER_MEDIUM = "10"
    VISUALIZER_LARGE = "15"
    
    # Отступы для Notebook
    NOTEBOOK_MAIN = "10"  # Основной отступ Notebook от краев окна
    NOTEBOOK_TAB_CONTENT = "5"  # Отступ содержимого вкладки


@dataclass
class UIConfig:
    """Общая конфигурация UI для объединенного приложения"""
    colors = UIColorScheme()
    fonts = UIFontScheme()
    sizes = UISizeScheme()
    padding = UIPaddingScheme()


# Создаем глобальный экземпляр конфигурации
UI_CONFIG = UIConfig()