import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
import os
from typing import List

from app.GraphService import GraphService
from app.DataTypes import GraphRequest, GraphTags, GraphSize


class GraphSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Search System")
        self.root.geometry("1000x800")  # Увеличил размер окна

        # Настройка логирования
        self.setup_logging()

        self.graph_service = GraphService()
        self.current_results: List[str] = []
        self.selected_graphs: set = set()  # Множество выбранных графов

        # Стиль для увеличения чекбоксов
        self.setup_styles()

        self.setup_ui()
        self.load_meta_data()

    def setup_styles(self):
        """Настройка стилей для увеличенных чекбоксов"""
        style = ttk.Style()
        style.configure('Large.TCheckbutton', font=('Arial', 10))
        style.configure('Large.Treeview', font=('Arial', 10))
        style.configure('Large.Treeview.Heading', font=('Arial', 10, 'bold'))

    def setup_logging(self):
        """Настройка логирования в файл"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, "log.txt")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # Также выводим в консоль
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== Graph Search Application Started ===")

    def setup_ui(self):
        """Создание интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов строк и колонок для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Система поиска графов",
                                font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))

        # Секция поиска по автору
        author_frame = ttk.LabelFrame(main_frame, text="Поиск по автору", padding="8")
        author_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        author_frame.columnconfigure(1, weight=1)

        ttk.Label(author_frame, text="Автор:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.author_entry = ttk.Entry(author_frame, font=('Arial', 10))
        self.author_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 15))

        self.strict_search_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(author_frame, text="Строгий поиск",
                        variable=self.strict_search_var, style='Large.TCheckbutton').grid(row=0, column=2)

        # Секция размера графа
        size_frame = ttk.LabelFrame(main_frame, text="Размер графа", padding="8")
        size_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        self.size_var = tk.StringVar()
        sizes = [("Любой", ""), ("Маленький", "small"), ("Средний", "medium"),
                 ("Большой", "large"), ("Огромный", "huge")]

        for i, (text, value) in enumerate(sizes):
            ttk.Radiobutton(size_frame, text=text, variable=self.size_var,
                            value=value, style='Large.TCheckbutton').grid(row=0, column=i, padx=8)

        # Секция свойств графа
        tags_frame = ttk.LabelFrame(main_frame, text="Свойства графа", padding="8")
        tags_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        # Первая строка свойств
        self.directed_var = tk.BooleanVar()
        self.weighted_var = tk.BooleanVar()
        self.connected_var = tk.BooleanVar()
        self.mixed_var = tk.BooleanVar()

        ttk.Checkbutton(tags_frame, text="Направленный", variable=self.directed_var,
                        style='Large.TCheckbutton').grid(row=0, column=0, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Взвешенный", variable=self.weighted_var,
                        style='Large.TCheckbutton').grid(row=0, column=1, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Связный", variable=self.connected_var,
                        style='Large.TCheckbutton').grid(row=0, column=2, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Смешанный", variable=self.mixed_var,
                        style='Large.TCheckbutton').grid(row=0, column=3, sticky=tk.W, padx=8, pady=3)

        # Вторая строка свойств
        self.full_var = tk.BooleanVar()
        self.double_var = tk.BooleanVar()
        self.simple_var = tk.BooleanVar()
        self.empty_var = tk.BooleanVar()

        ttk.Checkbutton(tags_frame, text="Полный", variable=self.full_var,
                        style='Large.TCheckbutton').grid(row=1, column=0, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Двудольный", variable=self.double_var,
                        style='Large.TCheckbutton').grid(row=1, column=1, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Простой", variable=self.simple_var,
                        style='Large.TCheckbutton').grid(row=1, column=2, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Пустой", variable=self.empty_var,
                        style='Large.TCheckbutton').grid(row=1, column=3, sticky=tk.W, padx=8, pady=3)

        # Третья строка свойств
        self.planar_var = tk.BooleanVar()
        self.tree_var = tk.BooleanVar()
        self.pseudo_var = tk.BooleanVar()

        ttk.Checkbutton(tags_frame, text="Планарный", variable=self.planar_var,
                        style='Large.TCheckbutton').grid(row=2, column=0, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Дерево", variable=self.tree_var,
                        style='Large.TCheckbutton').grid(row=2, column=1, sticky=tk.W, padx=8, pady=3)
        ttk.Checkbutton(tags_frame, text="Псевдограф", variable=self.pseudo_var,
                        style='Large.TCheckbutton').grid(row=2, column=2, sticky=tk.W, padx=8, pady=3)

        # Кнопки действий
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Поиск", command=self.search_graphs,
                   width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="Очистить", command=self.clear_form,
                   width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="Скачать выбранные", command=self.download_selected,
                   width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="Скачать все найденные", command=self.download_all,
                   width=18).pack(side=tk.LEFT, padx=8)

        # Фрейм для чекбокса "Выбрать всё"
        select_all_frame = ttk.Frame(main_frame)
        select_all_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))

        self.select_all_var = tk.BooleanVar()
        self.select_all_cb = ttk.Checkbutton(
            select_all_frame,
            text="ВЫБРАТЬ ВСЁ",
            variable=self.select_all_var,
            command=self.toggle_select_all,
            style='Large.TCheckbutton',
            width=15
        )
        self.select_all_cb.pack(side=tk.LEFT)

        # Результаты поиска
        results_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="8")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)

        # Создаем Treeview для отображения результатов с чекбоксами
        columns = ("selected", "name", "author", "size", "properties")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=18,
                                         style='Large.Treeview')

        self.results_tree.heading("selected", text="✓")
        self.results_tree.heading("name", text="Название графа")
        self.results_tree.heading("author", text="Автор")
        self.results_tree.heading("size", text="Размер")
        self.results_tree.heading("properties", text="Свойства")

        self.results_tree.column("selected", width=50, stretch=False, anchor='center')  # Увеличил ширину
        self.results_tree.column("name", width=250)
        self.results_tree.column("author", width=180)
        self.results_tree.column("size", width=120)
        self.results_tree.column("properties", width=300)

        # Привязываем обработчик клика для чекбоксов
        self.results_tree.bind('<Button-1>', self.on_tree_click)

        # Scrollbar для Treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, font=('Arial', 10))
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

    def on_tree_click(self, event):
        """Обработчик клика по дереву для чекбоксов"""
        item = self.results_tree.identify_row(event.y)
        column = self.results_tree.identify_column(event.x)

        if item and column == "#1":  # Колонка с чекбоксами
            values = self.results_tree.item(item)['values']
            graph_name = values[1]  # Имя графа во второй колонке

            # Переключаем состояние
            if graph_name in self.selected_graphs:
                self.selected_graphs.remove(graph_name)
                self.results_tree.set(item, "selected", "□")
            else:
                self.selected_graphs.add(graph_name)
                self.results_tree.set(item, "selected", "✓")

            # Обновляем состояние "Выбрать всё"
            self.update_select_all_state()

    def toggle_select_all(self):
        """Переключение состояния 'Выбрать всё'"""
        if self.select_all_var.get():
            # Выбираем все графы
            self.selected_graphs = set(self.current_results)
            for item in self.results_tree.get_children():
                self.results_tree.set(item, "selected", "✓")
        else:
            # Снимаем выбор со всех графов
            self.selected_graphs.clear()
            for item in self.results_tree.get_children():
                self.results_tree.set(item, "selected", "□")

    def update_select_all_state(self):
        """Обновление состояния чекбокса 'Выбрать всё'"""
        total_count = len(self.current_results)
        selected_count = len(self.selected_graphs)

        if selected_count == 0:
            self.select_all_var.set(False)
        elif selected_count == total_count:
            self.select_all_var.set(True)
        else:
            # Частичный выбор - устанавливаем неопределенное состояние
            self.select_all_var.set(False)

    def load_meta_data(self):
        """Загрузка meta данных в отдельном потоке"""
        self.status_var.set("Загрузка meta данных...")
        self.logger.info("Начата загрузка meta данных")

        def load_task():
            success = self.graph_service.download_meta()
            if success:
                message = f"Meta данные загружены. Графов: {len(self.graph_service.meta_data)}"
                self.root.after(0, lambda: self.status_var.set(message))
                self.logger.info(message)
            else:
                self.root.after(0, lambda: self.status_var.set("Ошибка загрузки meta данных"))
                self.logger.error("Не удалось загрузить meta данные")
                messagebox.showerror("Ошибка", "Не удалось загрузить meta данные")

        threading.Thread(target=load_task, daemon=True).start()

    def search_graphs(self):
        """Выполнение поиска графов"""
        # Логируем параметры поиска
        search_params = {
            "author": self.author_entry.get().strip(),
            "strict_search": self.strict_search_var.get(),
            "size": self.size_var.get(),
            "tags": {
                "directed": self.directed_var.get(),
                "weighted": self.weighted_var.get(),
                "connected": self.connected_var.get(),
                "mixed": self.mixed_var.get(),
                "full": self.full_var.get(),
                "double": self.double_var.get(),
                "simple": self.simple_var.get(),
                "empty": self.empty_var.get(),
                "planar": self.planar_var.get(),
                "tree": self.tree_var.get(),
                "pseudo": self.pseudo_var.get()
            }
        }
        self.logger.info(f"Выполнение поиска с параметрами: {search_params}")

        # Создаем GraphTags из выбранных свойств
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

        # Получаем размер
        size_value = self.size_var.get()
        size = GraphSize(size_value) if size_value else None

        # Создаем запрос
        request = GraphRequest(
            author=self.author_entry.get().strip() or None,
            size=size,
            tags=tags if any([self.directed_var.get(), self.weighted_var.get(),
                              self.connected_var.get(), self.mixed_var.get(),
                              self.full_var.get(), self.double_var.get(),
                              self.simple_var.get(), self.empty_var.get(),
                              self.planar_var.get(), self.tree_var.get(),
                              self.pseudo_var.get()]) else None,
            strict_search=self.strict_search_var.get()
        )

        self.status_var.set("Выполняется поиск...")

        def search_task():
            try:
                results = self.graph_service.search(request)
                self.current_results = results
                self.selected_graphs.clear()  # Сбрасываем выбор при новом поиске

                # Логируем результат поиска
                self.logger.info(f"Поиск завершен. Найдено графов: {len(results)}")

                # Обновляем UI в основном потоке
                self.root.after(0, self.update_results, results)

            except Exception as e:
                error_msg = f"Ошибка при поиске: {e}"
                self.logger.error(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Ошибка", error_msg))
                self.root.after(0, lambda: self.status_var.set("Ошибка при поиске"))

        threading.Thread(target=search_task, daemon=True).start()

    def update_results(self, results: List[str]):
        """Обновление таблицы с результатами"""
        # Очищаем текущие данные
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Добавляем новые результаты
        for graph_name in results:
            graph_info = self.graph_service.get_graph_info(graph_name)
            if graph_info:
                author = graph_info.get('author', 'Неизвестно')
                size = graph_info.get('size', 'Неизвестно')

                # Форматируем свойства
                properties = graph_info.get('properties', {})
                prop_list = [key for key, value in properties.items() if value is True]
                properties_str = ", ".join(prop_list) if prop_list else "Нет свойств"

                # Добавляем строку с пустым чекбоксом
                self.results_tree.insert("", tk.END, values=(
                    "□",  # Пустой чекбокс
                    graph_name,
                    author,
                    size,
                    properties_str
                ))

        # Сбрасываем "Выбрать всё"
        self.select_all_var.set(False)
        self.status_var.set(f"Найдено графов: {len(results)}")

    def clear_form(self):
        """Очистка формы"""
        self.logger.info("Очистка формы поиска")

        self.author_entry.delete(0, tk.END)
        self.size_var.set("")

        # Сбрасываем все чекбоксы
        for var in [self.directed_var, self.weighted_var, self.connected_var,
                    self.mixed_var, self.full_var, self.double_var, self.simple_var,
                    self.empty_var, self.planar_var, self.tree_var, self.pseudo_var]:
            var.set(False)

        # Очищаем результаты
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.current_results.clear()
        self.selected_graphs.clear()
        self.select_all_var.set(False)
        self.status_var.set("Форма очищена")

    def download_selected(self):
        """Скачивание выбранных графов"""
        if not self.selected_graphs:
            messagebox.showwarning("Предупреждение", "Выберите графы для скачивания")
            return

        selected_list = list(self.selected_graphs)
        self.logger.info(f"Начато скачивание выбранных графов: {len(selected_list)} файлов")
        self.download_graphs(selected_list)

    def download_all(self):
        """Скачивание всех найденных графов"""
        if not self.current_results:
            messagebox.showwarning("Предупреждение", "Нет графов для скачивания")
            return

        self.logger.info(f"Начато скачивание всех найденных графов: {len(self.current_results)} файлов")
        self.download_graphs(self.current_results)

    def download_graphs(self, graph_names: List[str]):
        """Скачивание указанных графов с диалоговым окном сохранения"""
        if not graph_names:
            return

        # Диалоговое окно выбора места сохранения
        default_filename = f"graphs_{len(graph_names)}_files.zip"
        zip_path = filedialog.asksaveasfilename(
            title="Сохранить графы как...",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if not zip_path:  # Пользователь отменил сохранение
            self.status_var.set("Скачивание отменено")
            self.logger.info("Скачивание отменено пользователем")
            return

        self.status_var.set(f"Скачивание {len(graph_names)} графов...")

        def download_task():
            try:
                self.logger.info(f"Скачивание графов: {graph_names} в {zip_path}")

                # Передаем выбранный путь в download_zip
                zip_path_final = self.graph_service.download_zip(graph_names, zip_path)

                success_msg = f"Скачивание завершено: {zip_path_final}"
                self.root.after(0, lambda: self.status_var.set(success_msg))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успех",
                    f"Графы успешно скачаны!\n\n"
                    f"Файл: {os.path.basename(zip_path_final)}\n"
                    f"Путь: {zip_path_final}\n"
                    f"Графов: {len(graph_names)}"
                ))
                self.logger.info(success_msg)

            except Exception as e:
                error_msg = f"Ошибка при скачивании: {e}"
                self.logger.error(error_msg)
                self.root.after(0, lambda: self.status_var.set("Ошибка скачивания"))
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка скачивания",
                    f"Не удалось скачать графы:\n{error_msg}"
                ))

        threading.Thread(target=download_task, daemon=True).start()


def run_frontend():
    """Запуск фронтенд приложения"""
    root = tk.Tk()
    app = GraphSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_frontend()
