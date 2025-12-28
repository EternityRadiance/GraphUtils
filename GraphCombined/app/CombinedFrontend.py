import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os

from app.GraphFrontend import GraphSearchApp
from app.GraphVisualizerApp import GraphVisualizerApp
from app.ConsoleWidget import init_console, get_console
from app.config import CONFIG


class CombinedGraphApp:
    """Объединенное приложение с вкладками"""

    def __init__(self, root):
        self.root = root
        self.root.title("Graph System - Поиск и Визуализация Графов")

        # Устанавливаем минимальный размер окна
        self.root.minsize(1200, 700)

        # Устанавливаем начальный размер окна
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(1400, screen_width - 100)
        window_height = min(850, screen_height - 100)
        self.root.geometry(f"{window_width}x{window_height}")

        # Центрируем окно
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")

        # Устанавливаем основной фон
        self.root.configure(bg=CONFIG.UI.colors.BACKGROUND)

        # Настройка логирования
        self.setup_logging()

        # Консоль
        self.console = None
        self.init_console()

        # Создаем Notebook (вкладки)
        self.create_notebook()

        # Статус бар (без меню)
        self.create_status_bar()

        # Загрузка данных для поиска
        self.load_search_data()

    def setup_logging(self):
        """Настройка логирования"""
        log_dir = CONFIG.LOGS_DIR
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = log_dir / "combined_log.txt"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== Combined Graph Application Started ===")

    def init_console(self):
        """Инициализация консоли"""
        try:
            self.console = init_console()
            console = get_console()
            if console:
                console.log_system("Объединенный интерфейс инициализирован")
        except Exception as e:
            print(f"Ошибка инициализации консоли: {e}")

    def create_notebook(self):
        """Создание вкладок с исправленными стилями"""
        # Создаем стиль для вкладок с ЧЕРНЫМ текстом
        style = ttk.Style()

        # Стиль для обычных вкладок
        style.configure('Custom.TNotebook',
                        background=CONFIG.UI.colors.BACKGROUND,
                        tabmargins=[2, 5, 2, 0])

        style.configure('Custom.TNotebook.Tab',
                        background=CONFIG.UI.colors.BACKGROUND,
                        foreground='#000000',  # ЧЕРНЫЙ текст всегда
                        font=('Arial', 10, 'bold'),
                        padding=[15, 8])

        style.map('Custom.TNotebook.Tab',
                  background=[('selected', CONFIG.UI.colors.SECONDARY),
                              ('active', '#E6E6FA')],
                  foreground=[('selected', '#000000'),  # ИСПРАВЛЕНО: ЧЕРНЫЙ текст при выборе ✅
                              ('active', '#000000'),  # ЧЕРНЫЙ при наведении
                              ('!selected', '#000000')])  # ЧЕРНЫЙ в остальных случаях

        # Создаем Notebook
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(10, 40))

        # Вкладка 1: Поиск графов
        self.tab1_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1_frame, text='🔍 ПОИСК ГРАФОВ')

        # Вкладка 2: Визуализация
        self.tab2_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2_frame, text='📊 ВИЗУАЛИЗАЦИЯ')

        # Создаем приложения внутри вкладок
        self.create_tab1_app()
        self.create_tab2_app()

        # Привязываем переключение вкладок
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def create_tab1_app(self):
        """Создание приложения поиска графов в первой вкладке"""
        # Создаем фрейм для приложения поиска с правильным размером
        self.search_frame = tk.Frame(self.tab1_frame, bg=CONFIG.UI.colors.BACKGROUND)
        self.search_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Настраиваем адаптивность
        self.search_frame.grid_rowconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)

        # Инициализируем приложение поиска
        self.search_app = GraphSearchApp(self.search_frame, embedded=True)

        # Добавляем кнопку для открытия в визуализаторе
        self.add_open_in_visualizer_button()

    def create_tab2_app(self):
        """Создание приложения визуализации во второй вкладке"""
        # Создаем фрейм для приложения визуализации с правильным размером
        self.visualizer_frame = tk.Frame(self.tab2_frame, bg=CONFIG.UI.colors.BACKGROUND)
        self.visualizer_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Настраиваем адаптивность
        self.visualizer_frame.grid_rowconfigure(0, weight=1)
        self.visualizer_frame.grid_columnconfigure(0, weight=1)

        # Инициализируем приложение визуализации
        self.visualizer_app = GraphVisualizerApp(self.visualizer_frame, embedded=True)

    def add_open_in_visualizer_button(self):
        """Добавляет кнопку для открытия графа в визуализаторе"""
        # Создаем фрейм для дополнительных кнопок
        extra_buttons_frame = tk.Frame(self.tab1_frame, bg=CONFIG.UI.colors.BACKGROUND)
        extra_buttons_frame.pack(fill='x', padx=10, pady=(0, 10))

        # Кнопка для открытия в визуализаторе
        self.open_in_visualizer_btn = ttk.Button(
            extra_buttons_frame,
            text="📂 ОТКРЫТЬ В ВИЗУАЛИЗАТОРЕ",
            command=self.open_selected_in_visualizer,
            style='Action.TButton'
        )
        self.open_in_visualizer_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка переключения на визуализатор
        self.switch_to_visualizer_btn = ttk.Button(
            extra_buttons_frame,
            text="➡ ПЕРЕЙТИ К ВИЗУАЛИЗАЦИИ",
            command=self.switch_to_visualizer_tab,
            style='Action.TButton'
        )
        self.switch_to_visualizer_btn.pack(side=tk.LEFT, padx=5)

    def create_status_bar(self):
        """Создание статус бара (без меню)"""
        status_frame = tk.Frame(self.root, bg=CONFIG.UI.colors.STATUS_BAR, height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_bar = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style='Status.TLabel',
            anchor=tk.W,
            padding=(10, 5)
        )
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)

        # Добавляем информацию о текущей вкладке справа
        self.tab_info_var = tk.StringVar(value="[Поиск графов]")
        tab_info_label = ttk.Label(
            status_frame,
            textvariable=self.tab_info_var,
            style='Status.TLabel',
            anchor=tk.E,
            padding=(10, 5)
        )
        tab_info_label.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=2)

    def load_search_data(self):
        """Загрузка данных для поиска"""

        def load_task():
            console = get_console()
            if console:
                console.log_info("Загрузка meta данных для поиска...")

        import threading
        threading.Thread(target=load_task, daemon=True).start()

    def toggle_console(self):
        """Переключение видимости консоли"""
        console = get_console()
        if console:
            console.toggle_visibility()

    def open_selected_in_visualizer(self):
        """Открыть выбранный граф в визуализаторе"""
        console = get_console()

        if not hasattr(self.search_app, 'selected_graphs') or not self.search_app.selected_graphs:
            if console:
                console.log_warning("Не выбран ни один граф для открытия")
            self.status_var.set("Выберите графы для открытия в визуализаторе")
            return

        selected_graphs = list(self.search_app.selected_graphs)

        if console:
            console.log_info(f"Открытие {len(selected_graphs)} графов в визуализаторе")

        # Переключаемся на вкладку визуализации
        self.notebook.select(1)

        self.status_var.set(f"Выбрано {len(selected_graphs)} графов для визуализации")

        if console:
            console.log_info(f"Графы для визуализации: {', '.join(selected_graphs[:5])}")
            if len(selected_graphs) > 5:
                console.log_info(f"... и еще {len(selected_graphs) - 5} графов")

    def switch_to_visualizer_tab(self):
        """Переключиться на вкладку визуализации"""
        self.notebook.select(1)
        console = get_console()
        if console:
            console.log_info("Переключение на вкладку визуализации")

    def switch_to_search_tab(self):
        """Переключиться на вкладку поиска"""
        self.notebook.select(0)
        console = get_console()
        if console:
            console.log_info("Переключение на вкладку поиска")

    def on_tab_changed(self, event):
        """Обработчик смены вкладки"""
        tab_index = self.notebook.index(self.notebook.select())
        tab_names = ["Поиск графов", "Визуализация"]

        console = get_console()
        if console:
            console.log_info(f"Активна вкладка {tab_names[tab_index]}")

        self.status_var.set(f"Готов к работе - {tab_names[tab_index]}")
        self.tab_info_var.set(f"[{tab_names[tab_index].upper()}]")

    def show_about(self):
        """Показать информацию о программе"""
        about_text = "Визуализатор + загрузчик графов"

        tk.messagebox.showinfo("О программе", about_text)

    def run(self):
        """Запуск приложения"""
        console = get_console()
        if console:
            console.log_system("Объединенное приложение запущено")
            console.log_info("Используйте вкладки для переключения между функциями")

        self.status_var.set("Система готова к работе")


def run_combined_app():
    """Запуск объединенного приложения"""
    root = tk.Tk()
    app = CombinedGraphApp(root)

    # Обработка закрытия окна
    def on_closing():
        console = get_console()
        if console:
            console.log_system("Объединенное приложение завершено")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    app.run()
    root.mainloop()


if __name__ == "__main__":
    run_combined_app()
