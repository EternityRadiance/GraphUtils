import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import math
from collections import deque, defaultdict
from explorer import GraphExplorer
from graph_models import Graph


class GraphCanvas(tk.Canvas):
    """Canvas для отрисовки графов с управлением как в PyGame версии"""

    def __init__(self, master, on_vertex_selected=None, on_edge_selected=None, on_deselect=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg='white', highlightthickness=0)

        # Данные графа
        self.graph = None
        self.vertices = []
        self.edges = []
        self.vertex_positions = {}
        self.vertex_radius = 15
        self.edge_weights = {}

        # Состояние взаимодействия (как в PyGame)
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.dragging_vertex = None
        self.last_mouse_pos = (0, 0)

        # Выбранные элементы
        self.selected_vertex = None
        self.selected_edge = None

        # Оптимизация для больших графов
        self.show_labels = True
        self.simplified_view = False

        # Callback'и
        self.on_vertex_selected_callback = on_vertex_selected
        self.on_edge_selected_callback = on_edge_selected
        self.on_deselect_callback = on_deselect

        # Привязка событий
        self.bind("<ButtonPress-1>", self.on_mouse_down)
        self.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonPress-3>", self.on_right_click)
        self.bind("<MouseWheel>", self.on_mouse_wheel)

        # Для Linux
        self.bind("<Button-4>", self.on_mouse_wheel)
        self.bind("<Button-5>", self.on_mouse_wheel)

        # Кэш для подписей вершин (для оптимизации)
        self.vertex_labels = {}

    def load_graph(self, graph: Graph):
        """Загружает граф и отрисовывает его"""
        self.graph = graph
        self.vertices = list(range(1, graph.vertices + 1))
        self.edges = graph.edges_list
        self.vertex_positions = {}
        self.vertex_labels.clear()  # Очищаем кэш подписей

        # Извлечение весов ребер
        self.edge_weights = {}
        for edge in self.edges:
            if 'weight' in edge:
                key = (edge['source'], edge['target'])
                self.edge_weights[key] = edge['weight']

        # Автоматическое расположение вершин как в PyGame версии
        self.arrange_vertices()

        self.selected_vertex = None
        self.selected_edge = None

        self.redraw_graph()

    def arrange_vertices(self):
        """Автоматическое расположение вершин как в PyGame версии"""
        self.vertex_positions = {}
        num_vertices = len(self.vertices)

        # Определяем размеры canvas
        width = self.winfo_width() or 1000
        height = self.winfo_height() or 700

        GRAPH_AREA_WIDTH = width
        GRAPH_AREA_HEIGHT = height

        # Для очень больших графов используем случайное расположение
        if num_vertices > 1000:
            import random
            positions = set()
            min_distance = 50

            for vertex in self.vertices:
                attempts = 0
                while attempts < 100:
                    x = random.uniform(50, GRAPH_AREA_WIDTH - 50)
                    y = random.uniform(50, GRAPH_AREA_HEIGHT - 50)

                    too_close = False
                    for pos in positions:
                        if math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2) < min_distance:
                            too_close = True
                            break

                    if not too_close:
                        self.vertex_positions[vertex] = (x, y)
                        positions.add((x, y))
                        break
                    attempts += 1

                if vertex not in self.vertex_positions:
                    x = random.uniform(50, GRAPH_AREA_WIDTH - 50)
                    y = random.uniform(50, GRAPH_AREA_HEIGHT - 50)
                    self.vertex_positions[vertex] = (x, y)
            return

        # Для деревьев
        if self.is_tree():
            self.arrange_tree(GRAPH_AREA_WIDTH, GRAPH_AREA_HEIGHT)
            return

        # Для двудольных графов
        if self.is_bipartite():
            left_col = []
            right_col = []

            for i, vertex in enumerate(self.vertices):
                if i % 2 == 0:
                    left_col.append(vertex)
                else:
                    right_col.append(vertex)

            # Располагаем с отступами
            for i, vertex in enumerate(left_col):
                x = GRAPH_AREA_WIDTH * 0.25
                y = GRAPH_AREA_HEIGHT * (i + 1) / (len(left_col) + 1)
                self.vertex_positions[vertex] = (x, y)

            for i, vertex in enumerate(right_col):
                x = GRAPH_AREA_WIDTH * 0.75
                y = GRAPH_AREA_HEIGHT * (i + 1) / (len(right_col) + 1)
                self.vertex_positions[vertex] = (x, y)
        else:
            # По умолчанию - расположение по кругу
            self.arrange_vertices_circle(GRAPH_AREA_WIDTH, GRAPH_AREA_HEIGHT)

    def arrange_tree(self, width, height):
        """Расположение для деревьев как в PyGame"""
        tree = self.build_tree_structure()
        root = self.find_tree_root(tree)

        # BFS для определения уровней
        levels = defaultdict(list)
        visited = set()
        queue = deque([(root, 0)])

        while queue:
            node, level = queue.popleft()
            if node in visited:
                continue

            visited.add(node)
            levels[level].append(node)

            for neighbor in tree[node]:
                if neighbor not in visited:
                    queue.append((neighbor, level + 1))

        # Располагаем вершины по уровням
        max_level = max(levels.keys()) if levels else 0

        for level in range(max_level + 1):
            vertices_in_level = levels[level]
            level_height = height * (level + 1) / (max_level + 2)

            for i, vertex in enumerate(vertices_in_level):
                level_width = width / (len(vertices_in_level) + 1)
                x = level_width * (i + 1)
                y = level_height
                self.vertex_positions[vertex] = (x, y)

    def build_tree_structure(self):
        """Строит структуру дерева из ребер"""
        tree = defaultdict(list)
        for edge in self.edges:
            tree[edge['source']].append(edge['target'])
            tree[edge['target']].append(edge['source'])
        return tree

    def find_tree_root(self, tree):
        """Находит корень дерева"""
        if not tree:
            return self.vertices[0] if self.vertices else 1

        max_degree = -1
        root = self.vertices[0]
        for vertex in self.vertices:
            degree = len(tree[vertex])
            if degree > max_degree:
                max_degree = degree
                root = vertex
        return root

    def arrange_vertices_circle(self, width, height):
        """Расположение по кругу как в PyGame"""
        center_x = width / 2
        center_y = height / 2

        # Динамический радиус
        base_radius = min(width, height) * 0.4

        # Увеличиваем радиус для больших графов
        if len(self.vertices) > 50:
            base_radius *= 2.0
        if len(self.vertices) > 100:
            base_radius *= 2.5
        if len(self.vertices) > 200:
            base_radius *= 3.0
        if len(self.vertices) > 500:
            base_radius *= 4.0

        radius = base_radius

        for i, vertex in enumerate(self.vertices):
            angle = 2 * math.pi * i / len(self.vertices)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.vertex_positions[vertex] = (x, y)

    def is_bipartite(self):
        if not self.graph:
            return False
        properties = getattr(self.graph, 'properties', {})
        if hasattr(properties, 'double'):
            return properties.double
        return False

    def is_tree(self):
        if not self.graph:
            return False
        properties = getattr(self.graph, 'properties', {})
        if hasattr(properties, 'tree'):
            return properties.tree
        return False

    def is_directed(self):
        if not self.graph:
            return False
        properties = getattr(self.graph, 'properties', {})
        if hasattr(properties, 'directed'):
            return properties.directed
        return False

    def is_weighted(self):
        if not self.graph:
            return False
        properties = getattr(self.graph, 'properties', {})
        if hasattr(properties, 'weighted'):
            return properties.weighted
        return any('weight' in edge for edge in self.edges)

    def redraw_graph(self):
        """Перерисовывает весь граф"""
        self.delete("all")

        if not self.graph or not self.vertex_positions:
            return

        is_large_graph = len(self.vertices) > 500

        # Сначала рисуем все ребра
        for i, edge in enumerate(self.edges):
            source = edge['source']
            target = edge['target']

            if source in self.vertex_positions and target in self.vertex_positions:
                start_pos = self.vertex_positions[source]
                end_pos = self.vertex_positions[target]

                # Применяем трансформации
                start_x = (start_pos[0] + self.offset_x) * self.scale
                start_y = (start_pos[1] + self.offset_y) * self.scale
                end_x = (end_pos[0] + self.offset_x) * self.scale
                end_y = (end_pos[1] + self.offset_y) * self.scale

                # Цвет ребра: синий для обычных, желтый для выделенных
                if self.selected_edge == i:
                    edge_color = 'yellow'
                    edge_width = 4
                else:
                    # ВСЕ невыделенные ребра синего цвета
                    edge_color = 'blue'
                    edge_width = 2 if is_large_graph else 3

                # Обработка петель
                if source == target:
                    # Рисуем эллипс (каплю) над вершиной
                    loop_width = 18 * self.scale
                    loop_height = 25 * self.scale

                    loop_rect = (
                        start_x - loop_width / 2,
                        start_y - loop_height,
                        start_x + loop_width / 2,
                        start_y
                    )
                    self.create_oval(loop_rect, outline=edge_color, width=edge_width)
                else:
                    # Обычное ребро
                    self.create_line(start_x, start_y, end_x, end_y,
                                     fill=edge_color, width=edge_width)

                    # Для направленных графов рисуем стрелку того же цвета
                    if self.is_directed() and not is_large_graph:
                        self.draw_arrow(start_x, start_y, end_x, end_y, edge_color)

        # Затем рисуем вершины поверх ребер
        for vertex, pos in self.vertex_positions.items():
            x = (pos[0] + self.offset_x) * self.scale
            y = (pos[1] + self.offset_y) * self.scale

            # Выбираем цвет вершины
            if vertex == self.selected_vertex:
                vertex_color = 'yellow'
                border_color = 'black'
                border_width = 3
            else:
                if is_large_graph:
                    vertex_color = 'red'
                elif self.is_bipartite():
                    vertex_color = 'red' if vertex % 2 == 0 else 'blue'
                elif self.is_tree():
                    vertex_color = 'green'
                else:
                    vertex_color = 'red'
                border_color = 'black'
                border_width = 1

            # Радиус вершины с учетом масштаба
            if is_large_graph:
                vertex_radius = max(3, int(8 * self.scale))
            else:
                vertex_radius = max(10, int(15 * self.scale))

            # Рисуем вершину
            self.create_oval(x - vertex_radius, y - vertex_radius,
                             x + vertex_radius, y + vertex_radius,
                             fill=vertex_color, outline=border_color,
                             width=border_width, tags=f'vertex_{vertex}')

            # Подпись вершины с правильным масштабированием
            if (not is_large_graph) or (is_large_graph and len(self.vertices) <= 1000):
                # Рассчитываем размер шрифта в зависимости от масштаба и размера вершины
                if is_large_graph:
                    base_font_size = 12
                else:
                    base_font_size = 24

                # Ограничиваем минимальный и максимальный размер шрифта
                font_size = int(base_font_size * min(max(self.scale, 0.5), 2.0))
                font_size = max(8, min(font_size, 36))  # Ограничиваем от 8 до 36

                # Создаем текст
                text_id = self.create_text(x, y, text=str(vertex),
                                           fill='white',
                                           font=('Arial', font_size),
                                           tags=f'label_{vertex}')
                self.vertex_labels[vertex] = text_id

    def draw_arrow(self, start_x, start_y, end_x, end_y, color):
        """Рисует стрелку для направленного ребра"""
        angle = math.atan2(end_y - start_y, end_x - start_x)
        arrow_length = 15 * self.scale

        tip_x = end_x - arrow_length * math.cos(angle)
        tip_y = end_y - arrow_length * math.sin(angle)

        left_x = tip_x - arrow_length * 0.5 * math.cos(angle - math.pi / 6)
        left_y = tip_y - arrow_length * 0.5 * math.sin(angle - math.pi / 6)
        right_x = tip_x - arrow_length * 0.5 * math.cos(angle + math.pi / 6)
        right_y = tip_y - arrow_length * 0.5 * math.sin(angle + math.pi / 6)

        self.create_polygon(end_x, end_y, left_x, left_y, right_x, right_y,
                            fill=color, outline=color)

    def on_mouse_down(self, event):
        """Обработчик нажатия кнопки мыши"""
        self.last_mouse_pos = (event.x, event.y)

        # Проверяем, кликнули ли на вершину
        clicked_vertex = None
        graph_mouse_x = (event.x / self.scale) - self.offset_x
        graph_mouse_y = (event.y / self.scale) - self.offset_y

        for vertex, pos in self.vertex_positions.items():
            distance = math.sqrt((graph_mouse_x - pos[0]) ** 2 + (graph_mouse_y - pos[1]) ** 2)
            vertex_radius = 15 if len(self.vertices) <= 500 else 8
            if distance <= vertex_radius * 1.5:  # Небольшой запас
                clicked_vertex = vertex
                break

        if clicked_vertex is not None:
            # Клик по вершине - начинаем перетаскивание
            self.dragging_vertex = clicked_vertex
        else:
            # Если не кликнули на вершину, начинаем перетаскивание всего графа
            self.dragging = True

    def on_mouse_up(self, event):
        """Обработчик отпускания кнопки мыши"""
        self.dragging = False
        self.dragging_vertex = None

    def on_mouse_drag(self, event):
        """Обработчик перемещения мыши с зажатой кнопкой"""
        dx = event.x - self.last_mouse_pos[0]
        dy = event.y - self.last_mouse_pos[1]

        if self.dragging_vertex:
            # Перемещаем вершину
            vertex = self.dragging_vertex
            if vertex in self.vertex_positions:
                x, y = self.vertex_positions[vertex]
                # Преобразуем смещение из экранных в координаты графа
                new_x = x + dx / self.scale
                new_y = y + dy / self.scale
                self.vertex_positions[vertex] = (new_x, new_y)

                # Перерисовываем граф
                self.redraw_graph()
        elif self.dragging:
            # Перемещаем весь граф
            self.offset_x += dx / self.scale
            self.offset_y += dy / self.scale
            self.redraw_graph()

        self.last_mouse_pos = (event.x, event.y)

    def on_right_click(self, event):
        """Обработчик правого клика для выбора элементов"""
        # Сначала проверяем вершины
        clicked_vertex = None
        graph_mouse_x = (event.x / self.scale) - self.offset_x
        graph_mouse_y = (event.y / self.scale) - self.offset_y

        for vertex, pos in self.vertex_positions.items():
            distance = math.sqrt((graph_mouse_x - pos[0]) ** 2 + (graph_mouse_y - pos[1]) ** 2)
            vertex_radius = 15 if len(self.vertices) <= 500 else 8
            if distance <= vertex_radius * 1.5:
                clicked_vertex = vertex
                break

        if clicked_vertex is not None:
            # Клик по вершине
            if self.selected_vertex == clicked_vertex:
                # Снимаем выделение при повторном клике
                self.deselect_all()
            else:
                self.select_vertex(clicked_vertex)
            return

        # Если не попали по вершине, проверяем ребра
        closest_edge = None
        min_distance = float('inf')

        for i, edge in enumerate(self.edges):
            source = edge['source']
            target = edge['target']

            if source in self.vertex_positions and target in self.vertex_positions:
                x1, y1 = self.vertex_positions[source]
                x2, y2 = self.vertex_positions[target]

                # Проверка на петлю
                if source == target:
                    # Для петель проверяем расстояние до эллипса
                    loop_center_x = x1
                    loop_center_y = y1 - 12.5  # Смещение центра эллипса

                    # Простая проверка расстояния до центра петли
                    distance = math.sqrt((graph_mouse_x - loop_center_x) ** 2 +
                                         (graph_mouse_y - loop_center_y) ** 2)

                    if distance < 20 and distance < min_distance:
                        min_distance = distance
                        closest_edge = i
                else:
                    # Для обычных ребер вычисляем расстояние до отрезка
                    distance = self.point_to_line_distance(graph_mouse_x, graph_mouse_y,
                                                           x1, y1, x2, y2)

                    if distance < 25 and distance < min_distance:
                        min_distance = distance
                        closest_edge = i

        if closest_edge is not None:
            # Клик по ребру
            if self.selected_edge == closest_edge:
                # Снимаем выделение при повторном клике
                self.deselect_all()
            else:
                self.select_edge(closest_edge)
        else:
            # Клик в пустое место
            self.deselect_all()

    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Вычисляет расстояние от точки до отрезка"""
        # Вектор отрезка
        dx = x2 - x1
        dy = y2 - y1

        # Если отрезок вырожден в точку
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # Параметр t проекции точки на прямую
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)

        # Ограничиваем t отрезком [0, 1]
        t = max(0, min(1, t))

        # Ближайшая точка на отрезке
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)

    def on_mouse_wheel(self, event):
        """Обработчик колесика мыши для масштабирования"""
        scale_factor = 1.1

        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Колесо вниз - уменьшаем масштаб
            self.scale /= scale_factor
            if self.scale < 0.1:
                self.scale = 0.1
        else:
            # Колесо вверх - увеличиваем масштаб
            self.scale *= scale_factor
            if self.scale > 10.0:
                self.scale = 10.0

        self.redraw_graph()

    def select_vertex(self, vertex):
        """Выбирает вершину"""
        self.deselect_all()
        self.selected_vertex = vertex
        self.redraw_graph()

        if self.on_vertex_selected_callback:
            self.on_vertex_selected_callback(vertex)

    def select_edge(self, edge_index):
        """Выбирает ребро"""
        self.deselect_all()
        self.selected_edge = edge_index
        self.redraw_graph()

        if self.on_edge_selected_callback and edge_index < len(self.edges):
            edge = self.edges[edge_index]
            self.on_edge_selected_callback((edge['source'], edge['target']))

    def deselect_all(self):
        """Снимает все выделения"""
        self.selected_vertex = None
        self.selected_edge = None
        self.redraw_graph()

        if self.on_deselect_callback:
            self.on_deselect_callback()

    def center_graph(self):
        """Центрирует граф на canvas"""
        if not self.vertex_positions:
            return

        # Сбрасываем трансформации
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Перерасполагаем вершины
        self.arrange_vertices()
        self.redraw_graph()

    def get_vertex_degree(self, vertex):
        """Вычисляет степень вершины"""
        degree = 0
        for edge in self.edges:
            if edge['source'] == vertex or edge['target'] == vertex:
                degree += 1
        return degree

    def get_vertex_neighbors(self, vertex):
        """Возвращает список соседей вершины"""
        neighbors = []
        for edge in self.edges:
            if edge['source'] == vertex:
                neighbors.append(edge['target'])
            elif edge['target'] == vertex:
                neighbors.append(edge['source'])
        return neighbors

    def get_vertex_edges(self, vertex):
        """Возвращает список ребер, связанных с вершиной"""
        vertex_edges = []
        for i, edge in enumerate(self.edges):
            if edge['source'] == vertex or edge['target'] == vertex:
                vertex_edges.append((i, edge))
        return vertex_edges


class GraphBrowser(ttk.Frame):
    """Браузер графов в ZIP-архиве с прокруткой"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.explorer = None
        self.graphs = {}
        self.current_file = None

        self.create_widgets()

    def create_widgets(self):
        """Создает виджеты браузера с прокруткой"""
        # Создаем основной контейнер с прокруткой
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True)

        # Создаем Canvas для прокрутки
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)

        # Контейнер для контента внутри Canvas
        self.scrollable_frame = ttk.Frame(canvas)

        # Настраиваем Canvas для прокрутки
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Создаем окно в Canvas для нашего фрейма
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Конфигурируем Canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Упаковываем элементы
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")



        # Список файлов
        self.listbox_frame = ttk.Frame(self.scrollable_frame)
        self.listbox_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Делаем Listbox фиксированной высоты
        self.listbox = tk.Listbox(self.listbox_frame,
                                  font=('Arial', 10),
                                  selectmode=tk.SINGLE,
                                  height=6)  # Фиксированная высота
        self.listbox.pack(side='left', fill='both', expand=True)

        listbox_scrollbar = ttk.Scrollbar(self.listbox_frame,
                                          orient='vertical',
                                          command=self.listbox.yview)
        listbox_scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=listbox_scrollbar.set)

        # Кнопка загрузки
        ttk.Button(self.scrollable_frame, text="Загрузить выбранный граф",
                   command=self.load_selected).pack(pady=10, padx=10)

        # Настраиваем растягивание окна при изменении размера
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

    def load_archive(self, path):
        """Загружает ZIP-архив"""
        self.explorer = GraphExplorer(path)
        files = self.explorer.list_files()
        json_files = [f for f in files if f.endswith('.json')]

        self.listbox.delete(0, tk.END)
        self.graphs.clear()

        for file in json_files:
            self.listbox.insert(tk.END, file)

        if json_files:
            self.listbox.selection_set(0)
            return len(json_files)
        return 0

    def load_selected(self):
        """Загружает выбранный граф"""
        selection = self.listbox.curselection()
        if not selection:
            return None

        filename = self.listbox.get(selection[0])
        self.current_file = filename

        if self.explorer:
            graph = self.explorer.read_graph(filename)
            if graph:
                return graph

        return None


class ScrollableFrame(ttk.Frame):
    """Кастомный фрейм с прокруткой для правой панели"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Создаем Canvas для прокрутки
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Контейнер для контента внутри Canvas
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Настраиваем Canvas для прокрутки
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Создаем окно в Canvas для нашего фрейма
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # Конфигурируем Canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Упаковываем элементы
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Настраиваем растягивание окна при изменении размера
        self.canvas.bind("<Configure>", self._configure_canvas)

    def _configure_canvas(self, event):
        """Обновляет ширину окна в Canvas при изменении размера"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)


class GraphVisualizerApp:
    """Главное приложение визуализатора графов"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Graph Visualizer")
        self.root.geometry("1600x900")

        self.graph = None
        self.explorer = None

        self.create_widgets()
        self.load_recent_file()

    def create_widgets(self):
        """Создает все виджеты интерфейса"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Левая панель - Canvas для графа
        left_frame = ttk.Frame(main_frame, width=1200)
        left_frame.pack(side='left', fill='both', expand=True)
        left_frame.pack_propagate(False)

        # Canvas для отрисовки графа
        self.canvas = GraphCanvas(
            left_frame,
            on_vertex_selected=self.on_vertex_selected,
            on_edge_selected=self.on_edge_selected,
            on_deselect=self.on_deselect,
            width=1200,
            height=700
        )
        self.canvas.pack(fill='both', expand=True)

        # Правая панель - управление с прокруткой
        right_frame = ScrollableFrame(main_frame, width=350)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)



        self.create_control_buttons(right_frame.scrollable_frame)
        self.create_graph_info_panel(right_frame.scrollable_frame)
        self.create_graph_browser(right_frame.scrollable_frame)
        self.create_selection_info_panel(right_frame.scrollable_frame)

    def create_control_buttons(self, parent):
        """Создает кнопки управления"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Открыть файл графа",
                   command=self.open_graph_file,
                   width=25).pack(pady=5)

        ttk.Button(button_frame, text="Открыть ZIP архив",
                   command=self.open_zip_archive,
                   width=25).pack(pady=5)

        ttk.Button(button_frame, text="Центрировать граф",
                   command=self.center_graph,
                   width=25).pack(pady=5)

        ttk.Button(button_frame, text="Выход",
                   command=self.root.quit,
                   width=25).pack(pady=20)

    def create_graph_info_panel(self, parent):
        """Создает панель информации о графе"""
        info_frame = ttk.LabelFrame(parent, text="Информация о графе", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)

        self.graph_info_text = scrolledtext.ScrolledText(info_frame,
                                                         height=10,  # Уменьшил высоту
                                                         font=('Arial', 9),
                                                         state='disabled')
        self.graph_info_text.pack(fill='both', expand=True)

    def create_graph_browser(self, parent):
        """Создает браузер графов для ZIP-архивов"""
        self.browser_frame = ttk.LabelFrame(parent, text="Архив графов", padding=10)
        self.browser_frame.pack_forget()  # Скрываем по умолчанию

        self.browser = GraphBrowser(self.browser_frame)
        self.browser.pack(fill='both', expand=True, padx=5, pady=5)

        self.browser.listbox.bind('<<ListboxSelect>>', self.on_graph_selected_in_browser)

    def create_selection_info_panel(self, parent):
        """Создает панель информации о выбранном элементе"""
        selection_frame = ttk.LabelFrame(parent, text="Выбранный элемент", padding=10)
        selection_frame.pack(fill='x', padx=10, pady=10)

        self.selection_info_text = scrolledtext.ScrolledText(selection_frame,
                                                             height=6,  # Уменьшил высоту
                                                             font=('Arial', 9),
                                                             state='disabled')
        self.selection_info_text.pack(fill='both', expand=True)

        self.on_deselect()

    def open_graph_file(self):
        """Открывает диалог выбора файла графа"""
        filetypes = [
            ("JSON файлы", "*.json"),
            ("ZIP архивы", "*.zip"),
            ("Все файлы", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Выберите файл графа",
            filetypes=filetypes,
            initialdir=os.getcwd()
        )

        if filename:
            self.load_file(filename)

    def open_zip_archive(self):
        """Открывает ZIP архив с графами"""
        filetypes = [
            ("ZIP архивы", "*.zip"),
            ("Все файлы", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Выберите ZIP архив",
            filetypes=filetypes,
            initialdir=os.getcwd()
        )

        if filename:
            self.load_zip_archive(filename)

    def load_file(self, filename):
        """Загружает файл графа"""
        try:
            if filename.endswith('.zip'):
                self.load_zip_archive(filename)
            else:
                explorer = GraphExplorer(os.path.dirname(filename))
                graph = explorer.read_graph(os.path.basename(filename))

                if graph:
                    self.set_graph(graph)
                    self.update_graph_info()
                    self.save_recent_file(filename)
                    self.hide_browser()
                else:
                    messagebox.showerror("Ошибка", "Не удалось загрузить граф из файла")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")

    def load_zip_archive(self, filename):
        """Загружает ZIP архив"""
        try:
            explorer = GraphExplorer(filename)
            files = explorer.list_files()
            json_files = [f for f in files if f.endswith('.json')]

            if not json_files:
                messagebox.showwarning("Внимание", "В архиве не найдено JSON файлов графов")
                return

            graph = explorer.read_graph(json_files[0])
            if graph:
                self.set_graph(graph)
                self.update_graph_info()
                self.show_browser()
                self.browser.load_archive(filename)
                self.save_recent_file(filename)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки архива: {str(e)}")

    def on_graph_selected_in_browser(self, event):
        """Обработчик выбора графа в браузере"""
        if self.browser:
            graph = self.browser.load_selected()
            if graph:
                self.set_graph(graph)
                self.update_graph_info()

    def set_graph(self, graph):
        """Устанавливает текущий граф"""
        self.graph = graph
        self.canvas.load_graph(graph)
        self.deselect_all()

    def update_graph_info(self):
        """Обновляет информацию о графе"""
        if not self.graph:
            return

        text = f"""АВТОР: {getattr(self.graph, 'author', 'Неизвестно')}

ОСНОВНАЯ ИНФОРМАЦИЯ:
• Вершин: {getattr(self.graph, 'vertices', 0)}
• Рёбер: {len(getattr(self.graph, 'edges_list', []))}
• Размер: {getattr(self.graph, 'size', 'Неизвестно')}
• Масштаб: {self.canvas.scale:.2f}

СВОЙСТВА ГРАФА:"""

        if hasattr(self.graph, 'properties'):
            props = self.graph.properties
            if hasattr(props, 'directed'):
                text += f"\n• Направленный: {'Да' if props.directed else 'Нет'}"
            if hasattr(props, 'weighted'):
                text += f"\n• Взвешенный: {'Да' if props.weighted else 'Нет'}"
            if hasattr(props, 'connected'):
                text += f"\n• Связный: {'Да' if props.connected else 'Нет'}"
            if hasattr(props, 'tree'):
                text += f"\n• Дерево: {'Да' if props.tree else 'Нет'}"
            if hasattr(props, 'double'):
                text += f"\n• Двудольный: {'Да' if props.double else 'Нет'}"
            if hasattr(props, 'planar'):
                text += f"\n• Планарный: {'Да' if props.planar else 'Нет'}"
            if hasattr(props, 'full'):
                text += f"\n• Полный: {'Да' if props.full else 'Нет'}"
            if hasattr(props, 'empty'):
                text += f"\n• Пустой: {'Да' if props.empty else 'Нет'}"

        self.graph_info_text.config(state='normal')
        self.graph_info_text.delete(1.0, tk.END)
        self.graph_info_text.insert(1.0, text)
        self.graph_info_text.config(state='disabled')

    def on_vertex_selected(self, vertex):
        """Обработчик выбора вершины"""
        if not self.graph:
            return

        pos = self.canvas.vertex_positions.get(vertex, (0, 0))
        text = f"""ВЕРШИНА: {vertex}

ИНФОРМАЦИЯ:
• Номер: {vertex}
• Позиция: ({pos[0]:.1f}, {pos[1]:.1f})
• Степень: {self.canvas.get_vertex_degree(vertex)}
• Соседи: {', '.join(map(str, self.canvas.get_vertex_neighbors(vertex)[:10]))}"""

        if len(self.canvas.get_vertex_neighbors(vertex)) > 10:
            text += f" ... (ещё {len(self.canvas.get_vertex_neighbors(vertex)) - 10})"

        self.selection_info_text.config(state='normal')
        self.selection_info_text.delete(1.0, tk.END)
        self.selection_info_text.insert(1.0, text)
        self.selection_info_text.config(state='disabled')

    def on_edge_selected(self, edge):
        """Обработчик выбора ребра"""
        if not self.graph:
            return

        source, target = edge

        text = f"""РЕБРО: {source} → {target}

ИНФОРМАЦИЯ:
• Источник: {source}
• Цель: {target}
• Тип: {'Петля' if source == target else 'Обычное ребро'}
• Направленное: {self.canvas.is_directed()}
• Вес: {self.canvas.edge_weights.get((source, target), '1.0')}"""

        self.selection_info_text.config(state='normal')
        self.selection_info_text.delete(1.0, tk.END)
        self.selection_info_text.insert(1.0, text)
        self.selection_info_text.config(state='disabled')

    def on_deselect(self):
        """Обработчик снятия выделения"""
        self.selection_info_text.config(state='normal')
        self.selection_info_text.delete(1.0, tk.END)
        self.selection_info_text.insert(1.0, "Выберите элемент графа для просмотра информации")
        self.selection_info_text.config(state='disabled')

    def center_graph(self):
        """Центрирует граф на canvas"""
        self.canvas.center_graph()

    def deselect_all(self):
        """Снимает все выделения"""
        self.canvas.deselect_all()
        self.on_deselect()

    def show_browser(self):
        """Показывает браузер графов"""
        self.browser_frame.pack(fill='x', padx=10, pady=(5, 5), anchor='n')

    def hide_browser(self):
        """Скрывает браузер графов"""
        self.browser_frame.pack_forget()

    def load_recent_file(self):
        """Загружает последний открытый файл"""
        recent_file = self.get_recent_file()
        if recent_file and os.path.exists(recent_file):
            pass

    def save_recent_file(self, filename):
        """Сохраняет информацию о последнем открытом файле"""
        try:
            with open('recent_files.json', 'w', encoding='utf-8') as f:
                json.dump({'last_file': filename}, f)
        except:
            pass

    def get_recent_file(self):
        """Возвращает последний открытый файл"""
        try:
            with open('recent_files.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('last_file')
        except:
            return None

    def run(self):
        """Запускает приложение"""
        self.root.mainloop()
