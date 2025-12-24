"""
Виджет консоли для отображения логов и статусов
"""
import tkinter as tk
from datetime import datetime
import threading
from typing import Optional
from app.config import CONFIG


class ConsoleWidget:
    def __init__(self, master=None):
        """
        Инициализация виджета консоли

        Args:
            master: Родительский виджет (если None, создается новое окно)
        """
        if master is None:
            self.window = tk.Toplevel()
            self.window.title("Консоль приложения")
            self.window.geometry("800x500")
            self.window.configure(bg=CONFIG.UI.colors.BACKGROUND)
            self.container = self.window
        else:
            self.window = None
            self.container = master

        self.setup_ui()
        self._buffer = []
        self._buffer_lock = threading.Lock()
        self._auto_scroll = True

        # Запускаем обработчик буфера
        self.process_buffer()

    def setup_ui(self):
        """Настройка интерфейса консоли"""
        # Заголовок
        title_frame = tk.Frame(self.container, bg=CONFIG.UI.colors.BACKGROUND)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        title_label = tk.Label(
            title_frame,
            text="📟 Консоль приложения",
            font=CONFIG.UI.fonts.TITLE,
            fg=CONFIG.UI.colors.PRIMARY,
            bg=CONFIG.UI.colors.BACKGROUND
        )
        title_label.pack(side=tk.LEFT)

        # Кнопки управления
        button_frame = tk.Frame(self.container, bg=CONFIG.UI.colors.BACKGROUND)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.clear_button = tk.Button(
            button_frame,
            text="Очистить консоль",
            command=self.clear_console,
            bg=CONFIG.UI.colors.SECONDARY,
            fg="white",
            font=CONFIG.UI.fonts.BUTTON,
            relief="flat",
            padx=10,
            pady=5
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

        # Чекбокс автопрокрутки
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(
            button_frame,
            text="Автопрокрутка",
            variable=self.auto_scroll_var,
            command=self.toggle_auto_scroll,
            bg=CONFIG.UI.colors.BACKGROUND,
            fg=CONFIG.UI.colors.PRIMARY,
            font=CONFIG.UI.fonts.LABEL,
            selectcolor=CONFIG.UI.colors.BACKGROUND
        )
        auto_scroll_check.pack(side=tk.LEFT)

        # Текстовое поле консоли
        console_frame = tk.Frame(self.container)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Полоса прокрутки
        scrollbar = tk.Scrollbar(console_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Основное текстовое поле
        self.console_text = tk.Text(
            console_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg="#1E1E1E",  # Темный фон для консоли
            fg="#D4D4D4",  # Светлый текст
            font=("Consolas", 10),
            borderwidth=1,
            relief="solid",
            state=tk.DISABLED
        )
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.console_text.yview)

        # Теги для разных типов сообщений
        self.console_text.tag_config("INFO", foreground="#4EC9B0")  # Голубовато-зеленый
        self.console_text.tag_config("SUCCESS", foreground="#6A9955")  # Зеленый
        self.console_text.tag_config("WARNING", foreground="#D7BA7D")  # Желтый
        self.console_text.tag_config("ERROR", foreground="#F44747")  # Красный
        self.console_text.tag_config("SYSTEM", foreground="#569CD6")  # Синий
        self.console_text.tag_config("TIME", foreground="#808080")  # Серый

        # Статус бар
        self.status_var = tk.StringVar(value="Консоль готова")
        status_bar = tk.Label(
            self.container,
            textvariable=self.status_var,
            bg=CONFIG.UI.colors.STATUS_BAR,
            fg=CONFIG.UI.colors.PRIMARY,
            font=CONFIG.UI.fonts.LABEL,
            anchor=tk.W,
            padx=10,
            pady=5
        )
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Защита от ввода
        self.console_text.bind("<Key>", lambda e: "break")

    def toggle_auto_scroll(self):
        """Переключение режима автопрокрутки"""
        self._auto_scroll = self.auto_scroll_var.get()

    def clear_console(self):
        """Очистка консоли"""
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete(1.0, tk.END)
        self.console_text.config(state=tk.DISABLED)
        self.status_var.set("Консоль очищена")

    def log(self, message: str, level: str = "INFO"):
        """
        Добавление сообщения в консоль

        Args:
            message: Текст сообщения
            level: Уровень сообщения (INFO, SUCCESS, WARNING, ERROR, SYSTEM)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        with self._buffer_lock:
            self._buffer.append((timestamp, message, level))

    def _process_buffer_item(self, timestamp: str, message: str, level: str):
        """Обработка одного элемента буфера"""
        self.console_text.config(state=tk.NORMAL)

        # Добавляем время
        self.console_text.insert(tk.END, f"[{timestamp}] ", "TIME")

        # Добавляем сообщение с соответствующим тегом
        self.console_text.insert(tk.END, message + "\n", level)

        # Автопрокрутка
        if self._auto_scroll:
            self.console_text.see(tk.END)

        self.console_text.config(state=tk.DISABLED)

    def process_buffer(self):
        """Периодическая обработка буфера сообщений"""
        with self._buffer_lock:
            if self._buffer:
                timestamp, message, level = self._buffer.pop(0)
                self.container.after(0, lambda: self._process_buffer_item(timestamp, message, level))

        # Планируем следующую проверку
        self.container.after(100, self.process_buffer)

    def log_info(self, message: str):
        """Логирование информационного сообщения"""
        self.log(message, "INFO")

    def log_success(self, message: str):
        """Логирование успешного события"""
        self.log(message, "SUCCESS")

    def log_warning(self, message: str):
        """Логирование предупреждения"""
        self.log(message, "WARNING")

    def log_error(self, message: str):
        """Логирование ошибки"""
        self.log(message, "ERROR")

    def log_system(self, message: str):
        """Логирование системного события"""
        self.log(message, "SYSTEM")

    def update_status(self, status: str):
        """Обновление статуса консоли"""
        self.status_var.set(status)

    def get_visible(self) -> bool:
        """Проверка, видно ли окно консоли"""
        if self.window:
            try:
                return self.window.winfo_viewable()
            except:
                return False
        return True

    def show(self):
        """Показать окно консоли"""
        if self.window:
            self.window.deiconify()

    def hide(self):
        """Скрыть окно консоли"""
        if self.window:
            self.window.withdraw()

    def toggle_visibility(self):
        """Переключение видимости окна консоли"""
        if self.window:
            if self.get_visible():
                self.hide()
            else:
                self.show()

    def destroy(self):
        """Уничтожение виджета консоли"""
        if self.window:
            self.window.destroy()


# Глобальный экземпляр консоли
_global_console: Optional[ConsoleWidget] = None


def init_console(master=None) -> ConsoleWidget:
    """
    Инициализация глобальной консоли

    Args:
        master: Родительский виджет

    Returns:
        Экземпляр ConsoleWidget
    """
    global _global_console
    if _global_console is None:
        _global_console = ConsoleWidget(master)
        _global_console.log_system("Консоль инициализирована")
    return _global_console


def get_console() -> Optional[ConsoleWidget]:
    """
    Получение глобальной консоли

    Returns:
        Экземпляр ConsoleWidget или None
    """
    return _global_console


def log(message: str, level: str = "INFO"):
    """Глобальная функция логирования"""
    console = get_console()
    if console:
        console.log(message, level)


def log_info(message: str):
    """Глобальная функция логирования информации"""
    log(message, "INFO")


def log_success(message: str):
    """Глобальная функция логирования успеха"""
    log(message, "SUCCESS")


def log_warning(message: str):
    """Глобальная функция логирования предупреждения"""
    log(message, "WARNING")


def log_error(message: str):
    """Глобальная функция логирования ошибки"""
    log(message, "ERROR")


def log_system(message: str):
    """Глобальная функция логирования системных событий"""
    log(message, "SYSTEM")
