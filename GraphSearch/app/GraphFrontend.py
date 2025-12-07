import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
import os
from typing import List

from app.GraphService import GraphService
from app.DataTypes import GraphRequest, GraphTags, GraphSize
from app.config import CONFIG


class GraphSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Search System")
        self.root.geometry(CONFIG.UI.sizes.WINDOW)
        
        # Устанавливаем основной фон окна
        self.root.configure(bg=CONFIG.UI.colors.BACKGROUND)

        # Настройка логирования
        self.setup_logging()

        self.graph_service = GraphService()
        self.current_results: List[str] = []
        self.selected_graphs: set = set()

        # Переменные для анимаций
        self.loading_active = False
        self.loading_dots = 0
        self.animation_running = False
        self.gradient_steps = CONFIG.UI.sizes.GRADIENT_STEPS
        self.gradient_speed = CONFIG.UI.sizes.GRADIENT_SPEED

        # Стиль для увеличения чекбоксов
        self.setup_styles()

        self.setup_ui()
        self.load_meta_data()

    def setup_logging(self):
        """Настройка логирования в файл"""
        log_dir = CONFIG.LOGS_DIR
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = log_dir / "log.txt"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== Graph Search Application Started ===")

    def setup_styles(self):
        """Настройка стилей с использованием конфига"""
        style = ttk.Style()
        
        # Конфигурация основных стилей
        style.configure('TFrame', background=CONFIG.UI.colors.BACKGROUND)
        
        # Стиль для рамок секций с разными цветами фона
        style.configure('Author.TLabelframe', 
                       background=CONFIG.UI.colors.AUTHOR_FRAME,
                       foreground=CONFIG.UI.colors.PRIMARY,
                       bordercolor='#D8BFD8',
                       borderwidth=1)
        
        style.configure('Size.TLabelframe', 
                       background=CONFIG.UI.colors.SIZE_FRAME,
                       foreground=CONFIG.UI.colors.PRIMARY,
                       bordercolor='#C9AFFF',
                       borderwidth=1)
        
        style.configure('Tags.TLabelframe', 
                       background=CONFIG.UI.colors.TAGS_FRAME,
                       foreground=CONFIG.UI.colors.PRIMARY,
                       bordercolor='#B19CD9',
                       borderwidth=1)
        
        style.configure('Results.TLabelframe', 
                       background=CONFIG.UI.colors.RESULTS_FRAME,
                       foreground=CONFIG.UI.colors.SECONDARY,
                       bordercolor='#A899E6',
                       borderwidth=1)
        
        style.configure('TLabelframe.Label', 
                       font=CONFIG.UI.fonts.HEADER)
        
        # Стиль для чекбоксов - ВСЕ используют одинаковые цвета!
        style.configure('Large.TCheckbutton',
                       font=CONFIG.UI.fonts.LABEL,
                       background=CONFIG.UI.colors.TAGS_FRAME,
                       foreground=CONFIG.UI.colors.PRIMARY)
        
        # Стиль для радиокнопок
        style.configure('Large.TRadiobutton',
                       font=CONFIG.UI.fonts.LABEL,
                       background=CONFIG.UI.colors.SIZE_FRAME,
                       foreground=CONFIG.UI.colors.PRIMARY)
        
        # Стиль для Treeview
        style.configure('Large.Treeview',
                       font=CONFIG.UI.fonts.TREEVIEW,
                       background='white',
                       foreground='#333333',
                       rowheight=25)
        
        style.configure('Large.Treeview.Heading',
                       font=CONFIG.UI.fonts.TREEVIEW_HEADER,
                       background=CONFIG.UI.colors.AUTHOR_FRAME,
                       foreground=CONFIG.UI.colors.PRIMARY)
        
        # Стиль для кнопок
        style.configure('Action.TButton',
                       font=CONFIG.UI.fonts.BUTTON,
                       background='#D8BFD8',
                       foreground='#4B0082',
                       borderwidth=1,
                       padding=(8, 6))
        
        style.map('Action.TButton',
                 background=[('active', CONFIG.UI.colors.SECONDARY), ('pressed', '#8A2BE2')],
                 foreground=[('active', '#000000'), ('pressed', '#000000')])
        
        # Стиль для статус бара
        style.configure('Status.TLabel',
                       font=CONFIG.UI.fonts.LABEL,
                       background=CONFIG.UI.colors.STATUS_BAR,
                       foreground=CONFIG.UI.colors.PRIMARY,
                       relief='sunken')

    def setup_ui(self):
        """Создание интерфейса с кнопками в правом верхнем углу"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding=CONFIG.UI.padding.LARGE)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Левая колонка (основная)
        main_frame.columnconfigure(1, weight=0)  # Правая колонка (кнопки)
        main_frame.rowconfigure(2, weight=1)  # Для таблицы результатов

        # Счетчик строк для grid
        current_row = 0

        # Верхняя строка: заголовок и поиск по автору
        top_frame = ttk.Frame(main_frame, style='TFrame')
        top_frame.grid(row=current_row, column=0, columnspan=2, 
                      sticky=(tk.W, tk.E), pady=(0, 10))
        current_row += 1
        
        # Заголовок в левом верхнем углу
        title_label = ttk.Label(top_frame, 
                               text="Система поиска графов",
                               font=CONFIG.UI.fonts.TITLE,
                               foreground=CONFIG.UI.colors.PRIMARY,
                               background=CONFIG.UI.colors.BACKGROUND)
        title_label.pack(side=tk.LEFT, padx=(0, 20))

        # Поиск по автору справа от заголовка
        author_subframe = ttk.Frame(top_frame, style='TFrame')
        author_subframe.pack(side=tk.LEFT, fill=tk.X, expand=True)

        author_label = ttk.Label(author_subframe, 
                                text="Автор:", 
                                font=CONFIG.UI.fonts.LABEL,
                                background=CONFIG.UI.colors.BACKGROUND,
                                foreground=CONFIG.UI.colors.PRIMARY)
        author_label.pack(side=tk.LEFT, padx=(0, 5))

        self.author_entry = ttk.Entry(author_subframe, 
                                     font=CONFIG.UI.fonts.ENTRY,
                                     width=CONFIG.UI.sizes.AUTHOR_ENTRY_WIDTH)
        self.author_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.strict_search_var = tk.BooleanVar(value=True)
        strict_check = ttk.Checkbutton(author_subframe, 
                                      text="Строгий поиск",
                                      variable=self.strict_search_var, 
                                      style='Large.TCheckbutton')
        strict_check.pack(side=tk.LEFT)

        # Кнопки в правом верхнем углу (в столбик)
        buttons_frame = ttk.Frame(main_frame, style='TFrame')
        buttons_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.N, tk.E), padx=(20, 0), pady=(0, 10))
        
        # Кнопки в столбик
        self.search_button = ttk.Button(buttons_frame, 
                                       text="ПОИСК", 
                                       command=self.search_graphs,
                                       style='Action.TButton',
                                       width=CONFIG.UI.sizes.BUTTON_WIDTH_NORMAL)
        self.search_button.pack(side=tk.TOP, pady=(0, 5), fill=tk.X)
        
        self.clear_button = ttk.Button(buttons_frame, 
                                      text="ОЧИСТИТЬ", 
                                      command=self.clear_form,
                                      style='Action.TButton',
                                      width=CONFIG.UI.sizes.BUTTON_WIDTH_NORMAL)
        self.clear_button.pack(side=tk.TOP, pady=5, fill=tk.X)
        
        self.download_selected_button = ttk.Button(buttons_frame, 
                                                  text="СКАЧАТЬ ВЫБРАННЫЕ", 
                                                  command=self.download_selected,
                                                  style='Action.TButton',
                                                  width=CONFIG.UI.sizes.BUTTON_WIDTH_NORMAL)
        self.download_selected_button.pack(side=tk.TOP, pady=5, fill=tk.X)
        
        self.download_all_button = ttk.Button(buttons_frame, 
                                             text="СКАЧАТЬ ВСЕ", 
                                             command=self.download_all,
                                             style='Action.TButton',
                                             width=CONFIG.UI.sizes.BUTTON_WIDTH_NORMAL)
        self.download_all_button.pack(side=tk.TOP, pady=(5, 0), fill=tk.X)

        # Два столбца: размер графа и свойства
        columns_frame = ttk.Frame(main_frame, style='TFrame')
        columns_frame.grid(row=current_row, column=0, 
                          sticky=(tk.W, tk.E), pady=(0, 15))
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.columnconfigure(1, weight=1)
        current_row += 1

        # Левый столбец: размер графа
        size_frame = ttk.LabelFrame(columns_frame, 
                                   text="РАЗМЕР ГРАФА", 
                                   padding=CONFIG.UI.padding.MEDIUM,
                                   style='Size.TLabelframe')
        size_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        self.size_var = tk.StringVar()
        sizes = [("Любой", ""), ("Маленький", "small"), ("Средний", "medium"),
                ("Большой", "large"), ("Огромный", "huge")]

        for i, (text, value) in enumerate(sizes):
            radio = ttk.Radiobutton(size_frame, 
                                   text=text, 
                                   variable=self.size_var,
                                   value=value, 
                                   style='Large.TRadiobutton')
            radio.grid(row=i, column=0, sticky=tk.W, pady=2)

        # Правый столбец: свойства графа
        tags_frame = ttk.LabelFrame(columns_frame, 
                                   text="СВОЙСТВА ГРАФА", 
                                   padding=CONFIG.UI.padding.MEDIUM,
                                   style='Tags.TLabelframe')
        tags_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка grid в tags_frame
        for i in range(6):
            tags_frame.grid_columnconfigure(i, weight=1, uniform="tag_col")

        # Переменные для чекбоксов
        self.directed_var = tk.BooleanVar()
        self.weighted_var = tk.BooleanVar()
        self.connected_var = tk.BooleanVar()
        self.mixed_var = tk.BooleanVar()
        self.full_var = tk.BooleanVar()
        self.double_var = tk.BooleanVar()
        self.simple_var = tk.BooleanVar()
        self.empty_var = tk.BooleanVar()
        self.planar_var = tk.BooleanVar()
        self.tree_var = tk.BooleanVar()
        self.pseudo_var = tk.BooleanVar()
        self.not_weighted_var = tk.BooleanVar()

        # Все чекбоксы используют одинаковый стиль
        checkbutton_config = {
            'style': 'Large.TCheckbutton',
        }

        # Первый столбец свойств
        row = 0
        col = 0
        
        ttk.Checkbutton(tags_frame, 
                       text="Направленный", 
                       variable=self.directed_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Взвешенный", 
                       variable=self.weighted_var,
                       command=self.on_weighted_changed,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Невзвешенный", 
                       variable=self.not_weighted_var,
                       command=self.on_not_weighted_changed,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Связный", 
                       variable=self.connected_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1

        # Второй столбец свойств
        row = 0
        col = 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Смешанный", 
                       variable=self.mixed_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Полный", 
                       variable=self.full_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Двудольный", 
                       variable=self.double_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Простой", 
                       variable=self.simple_var,
                       **checkbutton_config).grid(row=row, column=col)

        # Третий столбец свойств
        row = 0
        col = 2
        
        ttk.Checkbutton(tags_frame, 
                       text="Пустой", 
                       variable=self.empty_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Планарный", 
                       variable=self.planar_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Дерево", 
                       variable=self.tree_var,
                       **checkbutton_config).grid(row=row, column=col)
        row += 1
        
        ttk.Checkbutton(tags_frame, 
                       text="Псевдограф", 
                       variable=self.pseudo_var,
                       **checkbutton_config).grid(row=row, column=col)

        

        
        # Секция результатов поиска
        results_frame = ttk.LabelFrame(main_frame, 
                                      text="РЕЗУЛЬТАТЫ ПОИСКА", 
                                      padding=CONFIG.UI.padding.MEDIUM,
                                      style='Results.TLabelframe')
        results_frame.grid(row=current_row, column=0, columnspan=2, 
                          sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        current_row += 1

        # Создаем Treeview
        columns = ("selected", "name", "author", "size", "properties")
        self.results_tree = ttk.Treeview(results_frame, 
                                        columns=columns, 
                                        show="headings", 
                                        height=CONFIG.UI.sizes.RESULTS_TREE_HEIGHT,
                                        style='Large.Treeview')

        # Настройка заголовков
        self.results_tree.heading("selected", text="✓")
        self.results_tree.heading("name", text="Название графа")
        self.results_tree.heading("author", text="Автор")
        self.results_tree.heading("size", text="Размер")
        self.results_tree.heading("properties", text="Свойства")

        # Настройка ширины столбцов
        self.results_tree.column("selected", width=40, stretch=False, anchor='center')
        self.results_tree.column("name", width=250)
        self.results_tree.column("author", width=150)
        self.results_tree.column("size", width=100)
        self.results_tree.column("properties", width=350)

        # Цветовые теги для строк
        self.results_tree.tag_configure('oddrow', background=CONFIG.UI.colors.ODD_ROW)
        self.results_tree.tag_configure('evenrow', background=CONFIG.UI.colors.EVEN_ROW)
        self.results_tree.tag_configure('selected_row', background=CONFIG.UI.colors.SELECTED_ROW)

        # Привязываем обработчик клика
        self.results_tree.bind('<Button-1>', self.on_tree_click)

        # Scrollbar для Treeview
        scrollbar = ttk.Scrollbar(results_frame, 
                                 orient=tk.VERTICAL, 
                                 command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_bar = ttk.Label(main_frame, 
                                   textvariable=self.status_var, 
                                   style='Status.TLabel',
                                   anchor=tk.W,
                                   padding=(10, 5))
        self.status_bar.grid(row=current_row, column=0, columnspan=2, 
                            sticky=(tk.W, tk.E), pady=(5, 0))

    def on_weighted_changed(self):
        """Обработчик изменения чекбокса 'Взвешенный'"""
        if self.weighted_var.get():
            self.not_weighted_var.set(False)

    def on_not_weighted_changed(self):
        """Обработчик изменения чекбокса 'Невзвешенный'"""
        if self.not_weighted_var.get():
            self.weighted_var.set(False)

    # ========== УЛУЧШЕННЫЕ МЕТОДЫ ГРАДИЕНТНЫХ АНИМАЦИЙ ==========

    def animate_gradient_button(self, button, start_color='#D8BFD8', end_color='#9370DB'):
        """Анимация градиента для кнопки"""
        colors = self.generate_gradient(start_color, end_color, self.gradient_steps // 2)
        colors_back = self.generate_gradient(end_color, start_color, self.gradient_steps // 2)
        all_colors = colors + colors_back
        
        original_style = 'Action.TButton'
        temp_style_name = f'TempButtonStyle_{id(button)}'
        
        style = ttk.Style()
        
        def animate(step):
            if step < len(all_colors):
                try:
                    style.configure(temp_style_name,
                                   font=CONFIG.UI.fonts.BUTTON,
                                   background=all_colors[step],
                                   foreground='#4B0082',
                                   borderwidth=1,
                                   padding=(8, 6))
                    button.configure(style=temp_style_name)
                    self.root.after(self.gradient_speed, lambda: animate(step + 1))
                except:
                    pass
            else:
                button.configure(style=original_style)
        
        animate(0)

    def animate_process_gradient(self, target_color, final_text=None):
        """Анимация процесса с градиентом из бесцветного состояния в цветное и обратно"""
        if self.animation_running:
            return
            
        self.animation_running = True
        start_color = CONFIG.UI.colors.STATUS_BAR
        
        # Генерируем градиенты: из бесцветного в цветной и обратно
        colors_to_target = self.generate_gradient(start_color, target_color, self.gradient_steps // 2)
        colors_back = self.generate_gradient(target_color, start_color, self.gradient_steps // 2)
        all_colors = colors_to_target + colors_back
        
        def animate(step):
            if step < len(all_colors):
                try:
                    self.status_bar.configure(background=all_colors[step])
                    self.root.after(self.gradient_speed, lambda: animate(step + 1))
                except:
                    pass
            else:
                self.animation_running = False
                if final_text:
                    self.status_var.set(final_text)
        
        animate(0)

    def animate_success_gradient(self, final_text=None):
        """Анимация успеха с зелёным градиентом"""
        if self.animation_running:
            return
            
        self.animation_running = True
        start_color = CONFIG.UI.colors.STATUS_BAR
        target_color = CONFIG.UI.colors.SUCCESS_GRADIENT
        
        # Генерируем градиенты: из бесцветного в зелёный и обратно
        colors_to_target = self.generate_gradient(start_color, target_color, self.gradient_steps // 2)
        colors_back = self.generate_gradient(target_color, start_color, self.gradient_steps // 2)
        all_colors = colors_to_target + colors_back
        
        def animate(step):
            if step < len(all_colors):
                try:
                    self.status_bar.configure(background=all_colors[step])
                    self.root.after(self.gradient_speed, lambda: animate(step + 1))
                except:
                    pass
            else:
                self.animation_running = False
                if final_text:
                    self.status_var.set(final_text)
        
        animate(0)

    def animate_error_gradient(self, final_text=None):
        """Анимация ошибки с красным градиентом"""
        if self.animation_running:
            return
            
        self.animation_running = True
        start_color = CONFIG.UI.colors.STATUS_BAR
        target_color = CONFIG.UI.colors.ERROR_GRADIENT
        
        # Генерируем градиенты: из бесцветного в красный и обратно
        colors_to_target = self.generate_gradient(start_color, target_color, self.gradient_steps // 2)
        colors_back = self.generate_gradient(target_color, start_color, self.gradient_steps // 2)
        all_colors = colors_to_target + colors_back
        
        def animate(step):
            if step < len(all_colors):
                try:
                    self.status_bar.configure(background=all_colors[step])
                    self.root.after(self.gradient_speed, lambda: animate(step + 1))
                except:
                    pass
            else:
                self.animation_running = False
                if final_text:
                    self.status_var.set(final_text)
        
        animate(0)

    # ========== ОБНОВЛЁННЫЕ МЕТОДЫ С ГРАДИЕНТАМИ ==========

    def search_graphs(self):
        """Выполнение поиска графов"""
        # Анимация кнопки с градиентом
        self.animate_gradient_button(self.search_button)
        
        # Градиентная анимация процесса (жёлтый)
        self.status_var.set("Поиск...")
        self.animate_process_gradient(CONFIG.UI.colors.WARNING)
        self.start_loading_animation()
        
        # Проверяем взаимоисключающие свойства
        if self.weighted_var.get() and self.not_weighted_var.get():
            messagebox.showwarning("Предупреждение", 
                                 "Выбраны взаимоисключающие свойства 'Взвешенный' и 'Невзвешенный'")
            self.stop_loading_animation()
            self.status_var.set("Ошибка: взаимоисключающие свойства")
            self.animate_error_gradient()
            return
        
        tags = GraphTags(
            directed=self.directed_var.get() or None,
            weighted=self.weighted_var.get() or None,
            connected=self.connected_var.get() or None,
            mixed=self.mixed_var.get() or None,
            full=self.full_var.get() or None,
            double=self.double_var.get() or None,
            simple=self.simple_var.get() or None,
            empty=self.empty_var.get() or None,
            planar=self.planar_var.get() or None,
            tree=self.tree_var.get() or None,
            pseudo=self.pseudo_var.get() or None
        )

        size_value = self.size_var.get()
        size = GraphSize(size_value) if size_value else None

        request = GraphRequest(
            author=self.author_entry.get().strip() or None,
            size=size,
            tags=tags if any([self.directed_var.get(), self.weighted_var.get(),
                              self.connected_var.get(), self.mixed_var.get(),
                              self.full_var.get(), self.double_var.get(),
                              self.simple_var.get(), self.empty_var.get(),
                              self.planar_var.get(), self.tree_var.get(),
                              self.pseudo_var.get(), self.not_weighted_var.get()]) else None,
            strict_search=self.strict_search_var.get()
        )

        def search_task():
            try:
                results = self.graph_service.search(request)
                self.current_results = results
                self.selected_graphs.clear()

                self.logger.info(f"Поиск завершен. Найдено графов: {len(results)}")
                self.root.after(0, self.stop_loading_animation)
                self.root.after(0, self.update_results, results)

            except Exception as e:
                error_msg = f"Ошибка при поиске: {e}"
                self.logger.error(error_msg)
                self.root.after(0, self.stop_loading_animation)
                self.root.after(0, lambda: messagebox.showerror("Ошибка", error_msg))
                self.root.after(0, lambda: self.status_var.set("Ошибка поиска"))
                self.root.after(0, lambda: self.animate_error_gradient())

        threading.Thread(target=search_task, daemon=True).start()

    def clear_form(self):
        """Очистка формы"""
        self.logger.info("Очистка формы поиска")
        
        # Анимация кнопки с градиентом
        self.animate_gradient_button(self.clear_button)
        
        # Градиентная анимация процесса (жёлтый)
        self.status_var.set("Очистка...")
        self.animate_process_gradient(CONFIG.UI.colors.WARNING)
        
        # Очистка полей
        self.author_entry.delete(0, tk.END)
        self.size_var.set("")
        
        for var in [self.directed_var, self.weighted_var, self.connected_var,
                    self.mixed_var, self.full_var, self.double_var, self.simple_var,
                    self.empty_var, self.planar_var, self.tree_var, self.pseudo_var,
                    self.not_weighted_var]:
            var.set(False)
        
        # Очищаем внутренние данные
        self.current_results.clear()
        self.selected_graphs.clear()
        
        # Получаем количество графов для очистки
        children = list(self.results_tree.get_children())
        
        # Плавная очистка результатов с колбэком
        if children:
            def after_cleanup():
                self.status_var.set("Форма очищена")
                self.animate_success_gradient("Форма очищена")
            
            self.animate_clear_results(after_cleanup)
        else:
            # Если графов нет, сразу показываем успешное завершение
            def set_final_status():
                self.status_var.set("Форма очищена")
                self.animate_success_gradient("Форма очищена")
            
            self.root.after(500, set_final_status)

    def update_results(self, results: List[str]):
        """Обновление таблицы с результатами"""
        # Плавно очищаем старые результаты
        children = list(self.results_tree.get_children())
        
        def after_clear():
            # Добавляем новые результаты с анимацией
            self.add_results_with_animation(results)
        
        if children:
            self.animate_clear_results()
            self.root.after(len(children) * 30 + 200, after_clear)
        else:
            self.add_results_with_animation(results)

    def add_results_with_animation(self, results: List[str]):
        """Плавное добавление результатов"""
        self.current_results = results
        self.selected_graphs.clear()
        
        if not results:
            # Если результатов нет, сразу показываем сообщение
            self.status_var.set("Графы не найдены")
            self.animate_success_gradient("Графы не найдены")
            return
        
        for i, graph_name in enumerate(results):
            graph_info = self.graph_service.get_graph_info(graph_name)
            if graph_info:
                author = graph_info.get('author', 'Неизвестно')
                size = graph_info.get('size', 'Неизвестно')

                properties = graph_info.get('properties', {})
                prop_list = [key for key, value in properties.items() if value is True]
                properties_str = ", ".join(prop_list) if prop_list else "Нет свойств"

                row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'

                def add_row(idx=i, name=graph_name, auth=author, sz=size, props=properties_str, tag=row_tag):
                    item_id = self.results_tree.insert("", tk.END, 
                                                      values=("□", name, auth, sz, props))
                    self.animate_row_fade_in(item_id, tag)
                    
                    if idx == len(results) - 1:
                        self.results_tree.see(item_id)
                        # Градиентная анимация успешного завершения (зелёный)
                        self.status_var.set(f"Найдено графов: {len(results)}")
                        self.animate_success_gradient(f"Найдено графов: {len(results)}")
                
                self.root.after(i * 30, add_row)

    def download_selected(self):
        """Скачивание выбранных графов"""
        if not self.selected_graphs:
            messagebox.showwarning("Предупреждение", "Выберите графы для скачивания")
            return

        # Анимация кнопки с градиентом
        self.animate_gradient_button(self.download_selected_button)
        
        selected_list = list(self.selected_graphs)
        self.logger.info(f"Скачивание выбранных графов: {len(selected_list)}")
        self.download_graphs(selected_list)

    def download_all(self):
        """Скачивание всех найденных графов"""
        if not self.current_results:
            messagebox.showwarning("Предупреждение", "Нет графов для скачивания")
            return

        # Анимация кнопки с градиентом
        self.animate_gradient_button(self.download_all_button)
        
        self.logger.info(f"Скачивание всех графов: {len(self.current_results)}")
        self.download_graphs(self.current_results)

    def download_graphs(self, graph_names: List[str]):
        """Скачивание указанных графов"""
        default_filename = f"graphs_{len(graph_names)}_files.zip"
        zip_path = filedialog.asksaveasfilename(
            title="Сохранить графы как...",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if not zip_path:
            self.status_var.set("Скачивание отменено")
            self.animate_error_gradient()
            return

        self.status_var.set("Скачивание...")
        # Анимация процесса (фиолетовый градиент)
        self.animate_process_gradient(CONFIG.UI.colors.SECONDARY)
        self.start_loading_animation()

        def download_task():
            try:
                zip_path_final = self.graph_service.download_zip(graph_names, zip_path)
                success_msg = f"Скачивание завершено!"
                
                self.root.after(0, self.stop_loading_animation)
                self.root.after(0, lambda: self.status_var.set(success_msg))
                self.root.after(0, lambda: self.animate_success_gradient(success_msg))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успех",
                    f"Графы успешно скачаны!\n\nФайл: {os.path.basename(zip_path_final)}\nПуть: {zip_path_final}\nГрафов: {len(graph_names)}"
                ))
                
            except Exception as e:
                self.root.after(0, self.stop_loading_animation)
                self.root.after(0, lambda: self.status_var.set("Ошибка скачивания"))
                self.root.after(0, lambda: self.animate_error_gradient())
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось скачать графы:\n{e}"))

        threading.Thread(target=download_task, daemon=True).start()

    def load_meta_data(self):
        """Загрузка meta данных в отдельном потоке"""
        self.status_var.set("Загрузка meta данных...")
        self.animate_process_gradient(CONFIG.UI.colors.SECONDARY)
        self.logger.info("Начата загрузка meta данных")

        def load_task():
            success = self.graph_service.download_meta()
            if success:
                message = f"Meta данные загружены. Графов: {len(self.graph_service.meta_data)}"
                self.root.after(0, lambda: self.status_var.set(message))
                self.root.after(0, lambda: self.animate_success_gradient(message))
                self.logger.info(message)
            else:
                self.root.after(0, lambda: self.status_var.set("Ошибка загрузки"))
                self.root.after(0, lambda: self.animate_error_gradient())
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось загрузить meta данные"))

        threading.Thread(target=load_task, daemon=True).start()

    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========

    def on_tree_click(self, event):
        """Обработчик клика по дереву для чекбоксов"""
        item = self.results_tree.identify_row(event.y)
        column = self.results_tree.identify_column(event.x)

        if item and column == "#1":
            values = self.results_tree.item(item)['values']
            graph_name = values[1]

            if graph_name in self.selected_graphs:
                self.selected_graphs.remove(graph_name)
                self.results_tree.set(item, "selected", "□")
                item_index = self.results_tree.index(item)
                row_tag = 'evenrow' if item_index % 2 == 0 else 'oddrow'
                self.results_tree.item(item, tags=(row_tag,))
            else:
                self.selected_graphs.add(graph_name)
                self.results_tree.set(item, "selected", "✓")
                self.results_tree.item(item, tags=('selected_row',))

    def toggle_select_all(self):
        """Переключение состояния 'Выбрать всё'"""
        if hasattr(self, 'select_all_var'):
            if self.select_all_var.get():
                self.selected_graphs = set(self.current_results)
                for i, item in enumerate(self.results_tree.get_children()):
                    self.results_tree.set(item, "selected", "✓")
                    self.results_tree.item(item, tags=('selected_row',))
            else:
                self.selected_graphs.clear()
                for i, item in enumerate(self.results_tree.get_children()):
                    self.results_tree.set(item, "selected", "□")
                    row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    self.results_tree.item(item, tags=(row_tag,))

    def animate_row_fade_in(self, item_id, target_tag):
        """Плавное появление строки"""
        start_color = '#FFFFFF'
        
        if target_tag == 'evenrow':
            end_color = CONFIG.UI.colors.EVEN_ROW
        else:
            end_color = CONFIG.UI.colors.ODD_ROW
        
        colors = self.generate_gradient(start_color, end_color, 5)
        
        def fade_in(step):
            if step < len(colors):
                temp_tag = f'fadein_{item_id}_{step}'
                self.results_tree.tag_configure(temp_tag, background=colors[step])
                self.results_tree.item(item_id, tags=(temp_tag,))
                self.root.after(30, lambda: fade_in(step + 1))
            else:
                self.results_tree.item(item_id, tags=(target_tag,))
        
        fade_in(0)

    def animate_row_fade_out(self, item_id, callback=None):
        """Плавное исчезновение строки"""
        try:
            tags = self.results_tree.item(item_id, 'tags')
            if tags and len(tags) > 0:
                current_color = tags[0]
                
                if current_color == 'evenrow':
                    base_color = CONFIG.UI.colors.EVEN_ROW
                elif current_color == 'oddrow':
                    base_color = CONFIG.UI.colors.ODD_ROW
                elif current_color == 'selected_row':
                    base_color = CONFIG.UI.colors.SELECTED_ROW
                else:
                    base_color = '#FFFFFF'
                
                colors = self.generate_fade_colors(base_color, 5)
                
                def fade(step):
                    if step < len(colors):
                        temp_tag = f'fade_{item_id}_{step}'
                        self.results_tree.tag_configure(temp_tag, background=colors[step])
                        self.results_tree.item(item_id, tags=(temp_tag,))
                        self.root.after(30, lambda: fade(step + 1))
                    elif callback:
                        callback()
                
                fade(0)
        except:
            if callback:
                callback()

    def animate_clear_results(self, callback=None):
        """Плавная анимация очистки результатов"""
        children = list(self.results_tree.get_children())
        if not children:
            if callback:
                callback()
            return
        
        total_items = len(children)
        cleaned_count = [0]
        
        def remove_item(item, index):
            try:
                self.results_tree.delete(item)
            except:
                pass
            
            cleaned_count[0] += 1
            
            if cleaned_count[0] >= total_items and callback:
                callback()
        
        for i, item in enumerate(children):
            self.root.after(i * 30, 
                           lambda item=item, idx=i: 
                           self.animate_row_fade_out(item, lambda item=item, idx=idx: remove_item(item, idx)))

    def generate_gradient(self, start_color, end_color, steps=10):
        """Генерация градиента между двумя цветами"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        
        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)
        
        colors = []
        for i in range(steps):
            ratio = i / (steps - 1) if steps > 1 else 0
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            colors.append(rgb_to_hex((r, g, b)))
        
        return colors

    def generate_fade_colors(self, start_color, steps=5):
        """Генерация цветов для плавного исчезновения"""
        colors = self.generate_gradient(start_color, '#FFFFFF', steps)
        return colors

    def start_loading_animation(self):
        """Запуск анимации загрузки"""
        self.loading_active = True
        self.loading_dots = 0
        self.animate_loading_dots()

    def animate_loading_dots(self):
        """Анимация точек загрузки"""
        if self.loading_active:
            self.loading_dots = (self.loading_dots + 1) % 4
            current_text = self.status_var.get()
            base_text = current_text.rstrip('.')
            dots = '.' * self.loading_dots
            self.status_var.set(base_text + dots)
            self.root.after(400, self.animate_loading_dots)

    def stop_loading_animation(self):
        """Остановка анимации загрузки"""
        self.loading_active = False
        current_text = self.status_var.get()
        base_text = current_text.rstrip('.')
        self.status_var.set(base_text)


def run_frontend():
    """Запуск фронтенд приложения"""
    root = tk.Tk()
    app = GraphSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_frontend()