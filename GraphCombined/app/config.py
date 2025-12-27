import os
from dataclasses import dataclass
from pathlib import Path

from app.ui import UI_CONFIG


@dataclass
class AppConfig:
    """Основная конфигурация объединенного приложения"""
    # URL репозитория
    REPO_URL = "https://raw.githubusercontent.com/EternityRadiance/Graphs/main/data"
    BASE_SAVE_PATH = "./downloads"
    META_FILE_URL = "https://raw.githubusercontent.com/EternityRadiance/Graphs/main/meta.json"
    
    # UI конфигурация
    UI = UI_CONFIG
    
    # Настройки
    MAX_RETRIES = 3
    TIMEOUT = 10
    CHUNK_SIZE = 8192
    
    # Пути для визуализатора
    RECENT_FILES_PATH = "./recent_files.json"
    
    # Вычисляемые свойства
    @property
    def DOWNLOAD_DIR(self):
        return Path(self.BASE_SAVE_PATH)
    
    @property
    def LOGS_DIR(self):
        return Path("./logs")
    
    @property
    def META_FILE_PATH(self):
        return self.DOWNLOAD_DIR / "meta.json"
    
    @property
    def VISUALIZER_TEMP_DIR(self):
        temp_dir = Path("./temp_visualizer")
        temp_dir.mkdir(exist_ok=True)
        return temp_dir


# Создаем глобальный экземпляр конфигурации
CONFIG = AppConfig()

# Экспортируем основные константы для обратной совместимости
REPO_URL = CONFIG.REPO_URL
BASE_SAVE_PATH = CONFIG.BASE_SAVE_PATH
META_FILE_URL = CONFIG.META_FILE_URL
DOWNLOAD_DIR = CONFIG.DOWNLOAD_DIR
LOGS_DIR = CONFIG.LOGS_DIR
META_FILE_PATH = CONFIG.META_FILE_PATH