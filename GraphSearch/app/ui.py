"""
Конфигурация пользовательского интерфейса
"""

from dataclasses import dataclass


@dataclass
class UIColorScheme:
    """Цветовая схема приложения"""
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


@dataclass
class UIFontScheme:
    """Шрифтовая схема приложения"""
    TITLE = ("Arial", 12, "bold")
    HEADER = ("Arial", 10, "bold")
    LABEL = ("Arial", 9)
    BUTTON = ("Arial", 9, "bold")
    ENTRY = ("Arial", 9)
    TREEVIEW = ("Arial", 9)
    TREEVIEW_HEADER = ("Arial", 9, "bold")


@dataclass
class UISizeScheme:
    """Размерная схема приложения"""
    WINDOW = "1200x800"
    RESULTS_TREE_HEIGHT = 22
    AUTHOR_ENTRY_WIDTH = 30
    BUTTON_WIDTH_NORMAL = 20
    BUTTON_WIDTH_LARGE = 20
    
    # Анимации
    GRADIENT_STEPS = 12
    GRADIENT_SPEED = 40  # ms


@dataclass
class UIPaddingScheme:
    """Схема отступов"""
    SMALL = "5"
    MEDIUM = "10"
    LARGE = "15"


@dataclass
class UIConfig:
    """Общая конфигурация UI"""
    colors = UIColorScheme()
    fonts = UIFontScheme()
    sizes = UISizeScheme()
    padding = UIPaddingScheme()


# Создаем глобальный экземпляр конфигурации
UI_CONFIG = UIConfig()