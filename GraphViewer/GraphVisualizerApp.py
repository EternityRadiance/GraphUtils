import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import math
from collections import deque, defaultdict
from explorer import GraphExplorer
from graph_models import Graph


# Розово-лавандовая цветовая палитра
COLORS = {
    'bg_main': '#F5F0FF',
    'bg_panel': '#FFFFFF',
    'bg_canvas': '#FFFFFF',
    'accent': '#D8BFD8',
    'accent_dark': '#B19CD9',
    'text': '#333333',
    'text_light': '#666666',
    'border': '#E6E6FA',
    'button_bg': '#D8BFD8',
    'button_fg': '#333333',
    'button_hover': '#B19CD9',
    'vertex_normal': '#D8BFD8',
    'vertex_selected': '#FFD700',
    'edge_normal': '#9370DB',
    'edge_selected': '#FFD700',
    'animation_pulse': '#FF6B9D',
    'glow_effect': '#FFFACD',
}


class StyledButton(tk.Canvas):
    """Стилизованная кнопка с простыми анимациями"""
    def __init__(self, master, text, command, width=200, height=40, **kwargs):
        super().__init__(master, width=width, height=height, 
                         highlightthickness=0, bd=0, bg=COLORS['bg_main'])
        self.command = command
        self.button_text = text

        # Сохраняем размеры
        self.button_width = width
        self.button_height = height

        # Простая анимация цвета
        self.current_color = COLORS['button_bg']
        self.animation = None

        # Отрисовываем кнопку после создания
        self.after(10, self.draw_button)

        # Привязка событий
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def draw_button(self):
        """Рисует кнопку"""
        self.delete("all")

        # Используем сохраненные размеры
        width = self.button_width
        height = self.button_height

        # Простой прямоугольник с закругленными углами
        self.create_rectangle(0, 0, width, height, 
                             fill=self.current_color, 
                             outline=COLORS['border'], 
                             width=1)

        # Текст
        font_size = 11
        self.create_text(width//2, height//2, 
                        text=self.button_text, 
                        font=('Arial', font_size, 'bold'),
                        fill=COLORS['button_fg'])

    def animate_color(self, target_color, steps=10):
        """Простая анимация цвета"""
        if self.animation:
            self.after_cancel(self.animation)

        start_r, start_g, start_b = self.hex_to_rgb(self.current_color)
        target_r, target_g, target_b = self.hex_to_rgb(target_color)

        step = 0
        def animate():
            nonlocal step
            if step >= steps:
                self.current_color = target_color
                self.draw_button()
                return

            progress = step / steps
            r = int(start_r + (target_r - start_r) * progress)
            g = int(start_g + (target_g - start_g) * progress)
            b = int(start_b + (target_b - start_b) * progress)

            self.current_color = f'#{r:02x}{g:02x}{b:02x}'
            self.draw_button()

            step += 1
            self.animation = self.after(20, animate)

        animate()

    def hex_to_rgb(self, hex_color):
        """Конвертирует HEX цвет в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def on_press(self, event):
        """Нажатие кнопки"""
        self.animate_color(COLORS['accent_dark'], 5)

    def on_release(self, event):
        """Отпускание кнопки"""
        self.animate_color(COLORS['button_bg'], 10)
        if self.command:
            self.after(100, self.command)

    def on_enter(self, event):
        """Наведение курсора"""
        self.animate_color(COLORS['button_hover'], 5)

    def on_leave(self, event):
        """Уход курсора"""
        self.animate_color(COLORS['button_bg'], 10)


class GraphCanvas(tk.Canvas):
    """Canvas для отрисовки графов с улучшенными анимациями"""

    def __init__(self, master, on_vertex_selected=None, on_edge_selected=None, on_deselect=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=COLORS['bg_canvas'], highlightthickness=0)

        # Данные графа
        self.graph = None
        self.vertices = []
        self.edges = []
        self.vertex_positions = {}
        self.edge_weights = {}

        # Состояние взаимодействия
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.dragging_vertex = None
        self.last_mouse_pos = (0, 0)

        # Выбранные элементы
        self.selected_vertex = None
        self.selected_edge = None

        # Анимации
        self.active_animations = []
        self.vertex_animations = {}
        self.edge_animations = {}

        # Эффекты
        self.glow_effects = {}

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

    def load_graph(self, graph: Graph):
        """Загружает граф с улучшенной анимацией"""
        # Останавливаем все текущие анимации
        self.stop_all_animations()

        self.graph = graph
        self.vertices = list(range(1, graph.vertices + 1))
        self.edges = graph.edges_list
        self.vertex_positions = {}
        self.edge_weights = {}

        # Сбрасываем состояния
        self.vertex_animations = {}
        self.edge_animations = {}
        self.glow_effects = {}

        for edge in self.edges:
            if 'weight' in edge:
                key = (edge['source'], edge['target'])
                self.edge_weights[key] = edge['weight']

        self.arrange_vertices()
        self.selected_vertex = None
        self.selected_edge = None

        # Запускаем анимацию появления
        self.start_appearance_animation()

    def start_appearance_animation(self):
        """Запускает анимацию появления графа"""
        self.delete("all")

        # Получаем целевые позиции
        target_positions = self.vertex_positions.copy()

        # Определяем центр canvas
        center_x = self.winfo_width() / 2 if self.winfo_width() > 10 else 500
        center_y = self.winfo_height() / 2 if self.winfo_height() > 10 else 350

        # Устанавливаем все вершины в центре для начала анимации
        start_positions = {}
        for vertex in self.vertices:
            start_positions[vertex] = (center_x, center_y)

        # Сохраняем начальные позиции
        self.vertex_positions = start_positions.copy()

        # Рисуем все вершины в центре
        self.redraw_graph()

        # Анимируем движение вершин
        self.animate_vertices_to_target(target_positions)

    def animate_vertices_to_target(self, target_positions):
        """Анимирует движение вершин к целевым позициям"""
        start_positions = self.vertex_positions.copy()
        steps = 60
        current_step = 0

        def animate_step():
            nonlocal current_step
            if current_step >= steps:
                # Анимация завершена, запускаем анимацию ребер
                self.animate_edges_appearance()
                return

            progress = current_step / steps

            # Используем easing функцию для плавного движения
            ease_progress = progress * progress * (3 - 2 * progress)  # Кубический easing

            # Перемещаем каждую вершину
            for vertex in self.vertices:
                if vertex in start_positions and vertex in target_positions:
                    start_x, start_y = start_positions[vertex]
                    target_x, target_y = target_positions[vertex]

                    x = start_x + (target_x - start_x) * ease_progress
                    y = start_y + (target_y - start_y) * ease_progress

                    self.vertex_positions[vertex] = (x, y)

            # Перерисовываем
            self.redraw_graph()

            current_step += 1
            anim_id = self.after(30, animate_step)
            self.active_animations.append(anim_id)

        animate_step()

    def animate_edges_appearance(self):
        """Анимированное появление ребер"""
        # Сначала показываем все вершины
        self.delete("all")
        self.redraw_vertices_only()

        # Небольшая пауза перед появлением ребер
        self.after(200, self.animate_edges_drawing)

    def animate_edges_drawing(self):
        """Анимация рисования ребер"""
        total_edges = len(self.edges)

        # Рисуем все вершины в нормальном состоянии
        self.redraw_vertices_only()

        # Анимация ребер
        def draw_edges_wave(batch_start=0):
            if batch_start >= total_edges:
                # Все ребра нарисованы
                return

            # Рисуем группу ребер
            batch_size = min(2, total_edges - batch_start)
            for i in range(batch_start, batch_start + batch_size):
                edge = self.edges[i]
                self.animate_edge_drawing(edge, i)

            # Рекурсивно рисуем следующую группу
            delay = 150  # Задержка между группами
            anim_id = self.after(delay, lambda: draw_edges_wave(batch_start + batch_size))
            self.active_animations.append(anim_id)

        draw_edges_wave()

    def animate_edge_drawing(self, edge, edge_index):
        """Анимация рисования одного ребра"""
        source = edge['source']
        target = edge['target']

        if source not in self.vertex_positions or target not in self.vertex_positions:
            return

        start_pos = self.vertex_positions[source]
        end_pos = self.vertex_positions[target]

        start_x = (start_pos[0] + self.offset_x) * self.scale
        start_y = (start_pos[1] + self.offset_y) * self.scale
        end_x = (end_pos[0] + self.offset_x) * self.scale
        end_y = (end_pos[1] + self.offset_y) * self.scale

        # Вычисляем точки на границах вершин (не в центре)
        radius = 15  # Радиус вершины

        if source == target:
            # Для петель
            self.animate_loop_drawing(start_x, start_y, edge_index)
        else:
            # Для обычных ребер
            dx = end_x - start_x
            dy = end_y - start_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                # Нормализуем вектор
                dx_norm = dx / distance
                dy_norm = dy / distance

                # Точки на границах вершин
                adjusted_start_x = start_x + dx_norm * radius
                adjusted_start_y = start_y + dy_norm * radius
                adjusted_end_x = end_x - dx_norm * radius
                adjusted_end_y = end_y - dy_norm * radius

                self.animate_line_drawing(adjusted_start_x, adjusted_start_y, 
                                         adjusted_end_x, adjusted_end_y, edge_index)

    def animate_line_drawing(self, start_x, start_y, end_x, end_y, edge_index):
        """Анимация рисования линии ребра"""
        steps = 20
        current_step = 0

        def draw_line_step():
            nonlocal current_step
            if current_step >= steps:
                # После завершения анимации рисуем постоянное ребро
                self.create_line(start_x, start_y, end_x, end_y,
                               fill=COLORS['edge_normal'], width=2,
                               tags=f"edge_{edge_index}")
                return

            progress = current_step / steps

            # Текущая позиция конца линии
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress

            # Цвет меняется во время анимации
            if progress < 0.3:
                color = COLORS['animation_pulse']
            elif progress < 0.7:
                # Промежуточный цвет
                r = int(0xFF * (1 - progress/0.7) + 0x93 * (progress/0.7))
                g = int(0x6B * (1 - progress/0.7) + 0x70 * (progress/0.7))
                b = int(0x9D * (1 - progress/0.7) + 0xDB * (progress/0.7))
                color = f'#{r:02x}{g:02x}{b:02x}'
            else:
                color = COLORS['edge_normal']

            # Рисуем линию
            line_width = 3 if progress < 0.8 else 2

            self.create_line(start_x, start_y, current_x, current_y,
                           fill=color, width=line_width,
                           tags=f"edge_temp_{edge_index}")

            current_step += 1
            anim_id = self.after(30, draw_line_step)
            self.active_animations.append(anim_id)

        draw_line_step()

    def animate_loop_drawing(self, x, y, edge_index):
        """Анимация рисования петли"""
        steps = 25
        current_step = 0
        loop_width = 18 * self.scale
        loop_height = 25 * self.scale

        # Для петель используем точку на границе вершины
        loop_start_x = x
        loop_start_y = y - 15  # Начинаем от верхней границы вершины
        
        def draw_loop_step():
            nonlocal current_step
            if current_step >= steps:
                # Рисуем финальную петлю
                loop_rect = (
                    x - loop_width / 2,
                    y - loop_height,
                    x + loop_width / 2,
                    y - 15  # Заканчиваем у верхней границы вершины
                )
                self.create_oval(loop_rect, outline=COLORS['edge_normal'], width=2,
                               tags=f"edge_{edge_index}")
                return
            
            progress = current_step / steps
            
            # Анимируем рисование петли от 0 до 360 градусов
            angle = 2 * math.pi * progress
            
            # Вычисляем точки для части петли
            points = []
            for i in range(int(progress * 24) + 1):
                partial_angle = angle * (i / 24)
                px = x + (loop_width / 2) * math.cos(partial_angle)
                py = y - 15 - loop_height + (loop_height / 2) * math.sin(partial_angle)
                points.extend([px, py])
            
            if len(points) >= 4:
                # Цвет меняется во время анимации
                if progress < 0.5:
                    color = COLORS['animation_pulse']
                else:
                    color = COLORS['edge_normal']
                
                self.create_line(points, fill=color, width=2,
                               tags=f"edge_temp_{edge_index}", smooth=True)
            
            current_step += 1
            anim_id = self.after(40, draw_loop_step)
            self.active_animations.append(anim_id)
        
        draw_loop_step()

    def redraw_vertices_only(self):
        """Рисует только вершины (для анимации)"""
        for vertex, pos in self.vertex_positions.items():
            x = (pos[0] + self.offset_x) * self.scale
            y = (pos[1] + self.offset_y) * self.scale
            
            # Цвет вершины
            if vertex == self.selected_vertex:
                vertex_color = COLORS['vertex_selected']
                border_width = 2
            else:
                vertex_color = COLORS['vertex_normal']
                border_width = 1
            
            # Рисуем вершину
            self.create_oval(x - 15, y - 15,
                           x + 15, y + 15,
                           fill=vertex_color,
                           outline='black',
                           width=border_width)
            
            # Подпись
            self.create_text(x, y, text=str(vertex),
                           fill='white',
                           font=('Arial', 12, 'bold'))

    def arrange_vertices(self):
        """Расположение вершин"""
        self.vertex_positions = {}
        num_vertices = len(self.vertices)

        width = self.winfo_width() or 1000
        height = self.winfo_height() or 700

        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) * 0.35

        for i, vertex in enumerate(self.vertices):
            angle = 2 * math.pi * i / len(self.vertices)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.vertex_positions[vertex] = (x, y)

    def redraw_graph(self):
        """Перерисовывает граф"""
        self.delete("all")

        if not self.graph or not self.vertex_positions:
            return

        # Сначала рисуем ребра
        for i, edge in enumerate(self.edges):
            source = edge['source']
            target = edge['target']

            if source in self.vertex_positions and target in self.vertex_positions:
                start_pos = self.vertex_positions[source]
                end_pos = self.vertex_positions[target]

                start_x = (start_pos[0] + self.offset_x) * self.scale
                start_y = (start_pos[1] + self.offset_y) * self.scale
                end_x = (end_pos[0] + self.offset_x) * self.scale
                end_y = (end_pos[1] + self.offset_y) * self.scale

                if self.selected_edge == i:
                    edge_color = COLORS['edge_selected']
                    edge_width = 3
                else:
                    edge_color = COLORS['edge_normal']
                    edge_width = 2

                if source == target:
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
                    # Вычисляем точки на границах вершин
                    radius = 15
                    dx = end_x - start_x
                    dy = end_y - start_y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        # Нормализуем вектор
                        dx_norm = dx / distance
                        dy_norm = dy / distance
                        
                        # Точки на границах вершин
                        adjusted_start_x = start_x + dx_norm * radius
                        adjusted_start_y = start_y + dy_norm * radius
                        adjusted_end_x = end_x - dx_norm * radius
                        adjusted_end_y = end_y - dy_norm * radius
                        
                        self.create_line(adjusted_start_x, adjusted_start_y, 
                                       adjusted_end_x, adjusted_end_y,
                                       fill=edge_color, width=edge_width)

        # Рисуем вершины поверх ребер
        for vertex, pos in self.vertex_positions.items():
            x = (pos[0] + self.offset_x) * self.scale
            y = (pos[1] + self.offset_y) * self.scale

            if vertex == self.selected_vertex:
                vertex_color = COLORS['vertex_selected']
                border_width = 2
                
                # Статичное свечение для выбранной вершины
                self.create_oval(x-22, y-22, x+22, y+22,
                               outline='#FFD700',
                               width=2)
                self.create_oval(x-25, y-25, x+25, y+25,
                               outline='#FFFACD',
                               width=1)
            else:
                vertex_color = COLORS['vertex_normal']
                border_width = 1

            self.create_oval(x - 15, y - 15,
                           x + 15, y + 15,
                           fill=vertex_color,
                           outline='black',
                           width=border_width)

            self.create_text(x, y, text=str(vertex),
                           fill='white',
                           font=('Arial', 12, 'bold'))

    def on_mouse_down(self, event):
        """Нажатие мыши"""
        self.last_mouse_pos = (event.x, event.y)

        clicked_vertex = None
        graph_mouse_x = (event.x / self.scale) - self.offset_x
        graph_mouse_y = (event.y / self.scale) - self.offset_y

        for vertex, pos in self.vertex_positions.items():
            distance = math.sqrt((graph_mouse_x - pos[0]) ** 2 + (graph_mouse_y - pos[1]) ** 2)
            if distance <= 15:
                clicked_vertex = vertex
                break

        if clicked_vertex is not None:
            self.dragging_vertex = clicked_vertex
        else:
            self.dragging = True

    def on_mouse_up(self, event):
        """Отпускание мыши"""
        self.dragging = False
        self.dragging_vertex = None

    def on_mouse_drag(self, event):
        """Перетаскивание"""
        dx = event.x - self.last_mouse_pos[0]
        dy = event.y - self.last_mouse_pos[1]

        if self.dragging_vertex:
            vertex = self.dragging_vertex
            if vertex in self.vertex_positions:
                x, y = self.vertex_positions[vertex]
                new_x = x + dx / self.scale
                new_y = y + dy / self.scale
                self.vertex_positions[vertex] = (new_x, new_y)
                self.redraw_graph()
        elif self.dragging:
            self.offset_x += dx / self.scale
            self.offset_y += dy / self.scale
            self.redraw_graph()

        self.last_mouse_pos = (event.x, event.y)

    def on_right_click(self, event):
        """Правый клик для выбора"""
        clicked_vertex = None
        graph_mouse_x = (event.x / self.scale) - self.offset_x
        graph_mouse_y = (event.y / self.scale) - self.offset_y

        for vertex, pos in self.vertex_positions.items():
            distance = math.sqrt((graph_mouse_x - pos[0]) ** 2 + (graph_mouse_y - pos[1]) ** 2)
            if distance <= 15:
                clicked_vertex = vertex
                break

        if clicked_vertex is not None:
            if self.selected_vertex == clicked_vertex:
                self.deselect_all()
            else:
                self.animate_selection(clicked_vertex, None)
            return

        closest_edge = None
        min_distance = float('inf')

        for i, edge in enumerate(self.edges):
            source = edge['source']
            target = edge['target']

            if source in self.vertex_positions and target in self.vertex_positions:
                x1, y1 = self.vertex_positions[source]
                x2, y2 = self.vertex_positions[target]

                distance = self.point_to_line_distance(graph_mouse_x, graph_mouse_y,
                                                     x1, y1, x2, y2)

                if distance < 20 and distance < min_distance:
                    min_distance = distance
                    closest_edge = i

        if closest_edge is not None:
            if self.selected_edge == closest_edge:
                self.deselect_all()
            else:
                self.animate_selection(None, closest_edge)
        else:
            self.deselect_all()

    def animate_selection(self, vertex, edge):
        """Анимация выбора элемента"""
        old_vertex = self.selected_vertex
        old_edge = self.selected_edge
        
        # Анимация снятия старого выделения
        if old_vertex:
            self.animate_deselect_vertex(old_vertex)
        elif old_edge is not None:
            self.animate_deselect_edge(old_edge)
        
        # Небольшая пауза перед новым выделением
        def select_new():
            self.selected_vertex = vertex
            self.selected_edge = edge
            
            # Анимация нового выделения
            if vertex:
                self.animate_select_vertex(vertex)
            elif edge is not None:
                self.animate_select_edge(edge)
            
            self.redraw_graph()
            
            if vertex and self.on_vertex_selected_callback:
                self.on_vertex_selected_callback(vertex)
            elif edge is not None and self.on_edge_selected_callback:
                edge_data = self.edges[edge]
                self.on_edge_selected_callback((edge_data['source'], edge_data['target']))
        
        self.after(100, select_new)

    def animate_select_vertex(self, vertex):
        """Анимация выбора вершины"""
        if vertex not in self.vertex_positions:
            return
        
        pos = self.vertex_positions[vertex]
        x = (pos[0] + self.offset_x) * self.scale
        y = (pos[1] + self.offset_y) * self.scale
        
        # Эффект постепенного появления свечения
        steps = 6
        current_step = 0
        
        def glow_step():
            nonlocal current_step
            if current_step >= steps:
                # Окончательное свечение
                self.create_oval(x-22, y-22, x+22, y+22,
                               outline='#FFD700',
                               width=2,
                               tags=f"select_glow_{vertex}")
                self.create_oval(x-25, y-25, x+25, y+25,
                               outline='#FFFACD',
                               width=1,
                               tags=f"select_glow_{vertex}")
                return
            
            progress = current_step / steps
            
            # Плавное появление свечения
            radius = 15 + 7 * progress

            # Рисуем плавно появляющееся свечение
            self.delete(f"select_glow_{vertex}")
            self.create_oval(x - radius, y - radius,
                           x + radius, y + radius,
                           outline='#FFD700',
                           width=2,
                           tags=f"select_glow_{vertex}")

            current_step += 1
            anim_id = self.after(30, glow_step)
            self.active_animations.append(anim_id)

        glow_step()

    def animate_select_edge(self, edge_index):
        """Анимация выбора ребра"""
        if edge_index >= len(self.edges):
            return

        edge = self.edges[edge_index]
        source = edge['source']
        target = edge['target']

        if source not in self.vertex_positions or target not in self.vertex_positions:
            return

        start_pos = self.vertex_positions[source]
        end_pos = self.vertex_positions[target]

        start_x = (start_pos[0] + self.offset_x) * self.scale
        start_y = (start_pos[1] + self.offset_y) * self.scale
        end_x = (end_pos[0] + self.offset_x) * self.scale
        end_y = (end_pos[1] + self.offset_y) * self.scale

        # Эффект постепенного изменения ширины ребра
        steps = 5
        current_step = 0

        def thicken_step():
            nonlocal current_step
            if current_step >= steps:
                # Окончательная ширина
                self.delete(f"select_edge_{edge_index}")
                if source == target:
                    loop_width = 18 * self.scale
                    loop_height = 25 * self.scale
                    loop_rect = (
                        start_x - loop_width / 2,
                        start_y - loop_height,
                        start_x + loop_width / 2,
                        start_y
                    )
                    self.create_oval(loop_rect, outline=COLORS['edge_selected'], 
                                   width=3,
                                   tags=f"select_edge_{edge_index}")
                else:
                    # Вычисляем точки на границах вершин
                    radius = 15
                    dx = end_x - start_x
                    dy = end_y - start_y
                    distance = math.sqrt(dx*dx + dy*dy)

                    if distance > 0:
                        dx_norm = dx / distance
                        dy_norm = dy / distance

                        adjusted_start_x = start_x + dx_norm * radius
                        adjusted_start_y = start_y + dy_norm * radius
                        adjusted_end_x = end_x - dx_norm * radius
                        adjusted_end_y = end_y - dy_norm * radius
                        
                        self.create_line(adjusted_start_x, adjusted_start_y,
                                       adjusted_end_x, adjusted_end_y,
                                       fill=COLORS['edge_selected'], 
                                       width=3,
                                       tags=f"select_edge_{edge_index}")
                return

            progress = current_step / steps

            # Плавное увеличение ширины
            width = 2 + progress

            # Рисуем ребро с плавно увеличивающейся шириной
            self.delete(f"select_edge_{edge_index}")
            if source == target:
                loop_width = 18 * self.scale
                loop_height = 25 * self.scale
                loop_rect = (
                    start_x - loop_width / 2,
                    start_y - loop_height,
                    start_x + loop_width / 2,
                    start_y
                )
                self.create_oval(loop_rect, outline=COLORS['edge_selected'], 
                               width=int(width)+1,
                               tags=f"select_edge_{edge_index}")
            else:
                # Вычисляем точки на границах вершин
                radius = 15
                dx = end_x - start_x
                dy = end_y - start_y
                distance = math.sqrt(dx*dx + dy*dy)

                if distance > 0:
                    dx_norm = dx / distance
                    dy_norm = dy / distance

                    adjusted_start_x = start_x + dx_norm * radius
                    adjusted_start_y = start_y + dy_norm * radius
                    adjusted_end_x = end_x - dx_norm * radius
                    adjusted_end_y = end_y - dy_norm * radius

                    self.create_line(adjusted_start_x, adjusted_start_y,
                                   adjusted_end_x, adjusted_end_y,
                                   fill=COLORS['edge_selected'], 
                                   width=int(width)+1,
                                   tags=f"select_edge_{edge_index}")

            current_step += 1
            anim_id = self.after(40, thicken_step)
            self.active_animations.append(anim_id)

        thicken_step()

    def animate_deselect_vertex(self, vertex):
        """Анимация снятия выделения с вершины"""
        if vertex not in self.vertex_positions:
            return

        # Простая анимация исчезновения свечения
        steps = 4
        current_step = 0

        def fade_step():
            nonlocal current_step
            if current_step >= steps:
                self.delete(f"select_glow_{vertex}")
                return

            progress = current_step / steps

            current_step += 1
            anim_id = self.after(25, fade_step)
            self.active_animations.append(anim_id)

        fade_step()

    def animate_deselect_edge(self, edge_index):
        """Анимация снятия выделения с ребра"""
        steps = 4
        current_step = 0

        def fade_step():
            nonlocal current_step
            if current_step >= steps:
                self.delete(f"select_edge_{edge_index}")
                return

            current_step += 1
            anim_id = self.after(25, fade_step)
            self.active_animations.append(anim_id)

        fade_step()

    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Расстояние от точки до отрезка"""
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)

    def on_mouse_wheel(self, event):
        """Масштабирование с плавной анимацией относительно центра окна"""
        # Получаем текущий центр окна
        canvas_center_x = self.winfo_width() / 2
        canvas_center_y = self.winfo_height() / 2

        # Преобразуем центр канваса в координаты графа
        graph_center_x = (canvas_center_x / self.scale) - self.offset_x
        graph_center_y = (canvas_center_y / self.scale) - self.offset_y

        old_scale = self.scale
        scale_factor = 1.1

        if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Уменьшение
            self.scale /= scale_factor
            if self.scale < 0.1:
                self.scale = 0.1
        else:
            # Увеличение
            self.scale *= scale_factor
            if self.scale > 10.0:
                self.scale = 10.0

        # Вычисляем новые смещения, чтобы сохранить центр графа в центре окна
        new_canvas_center_x = canvas_center_x
        new_canvas_center_y = canvas_center_y

        # Находим новые смещения для сохранения центра
        self.offset_x = (new_canvas_center_x / self.scale) - graph_center_x
        self.offset_y = (new_canvas_center_y / self.scale) - graph_center_y

        # Плавная анимация масштабирования
        steps = 8
        current_step = 0

        def scale_step():
            nonlocal current_step
            if current_step >= steps:
                self.redraw_graph()
                return

            progress = current_step / steps
            ease_progress = progress * progress * (3 - 2 * progress)  # Кубический easing

            current_scale = old_scale + (self.scale - old_scale) * ease_progress

            # Плавно изменяем смещения для анимации
            current_offset_x = self.offset_x
            current_offset_y = self.offset_y

            # Для плавности можно также анимировать смещения, но это сложнее
            # Пока просто масштабируем
            temp_scale = self.scale
            temp_offset_x = self.offset_x
            temp_offset_y = self.offset_y

            self.scale = current_scale
            # Пересчитываем смещения для текущего масштаба
            self.offset_x = (canvas_center_x / current_scale) - graph_center_x
            self.offset_y = (canvas_center_y / current_scale) - graph_center_y

            self.redraw_graph()

            # Возвращаем исходные значения
            self.scale = temp_scale
            self.offset_x = temp_offset_x
            self.offset_y = temp_offset_y

            current_step += 1
            anim_id = self.after(25, scale_step)
            self.active_animations.append(anim_id)

        scale_step()

    def select_vertex(self, vertex):
        """Выбор вершины с анимацией"""
        self.deselect_all()
        self.selected_vertex = vertex
        self.animate_select_vertex(vertex)
        self.redraw_graph()

        if self.on_vertex_selected_callback:
            self.on_vertex_selected_callback(vertex)

    def select_edge(self, edge_index):
        """Выбор ребра с анимацией"""
        self.deselect_all()
        self.selected_edge = edge_index
        self.animate_select_edge(edge_index)
        self.redraw_graph()

        if self.on_edge_selected_callback and edge_index < len(self.edges):
            edge = self.edges[edge_index]
            self.on_edge_selected_callback((edge['source'], edge['target']))

    def deselect_all(self):
        """Снятие выделения с анимацией"""
        if self.selected_vertex:
            self.animate_deselect_vertex(self.selected_vertex)
        elif self.selected_edge is not None:
            self.animate_deselect_edge(self.selected_edge)

        self.selected_vertex = None
        self.selected_edge = None

        def delayed_redraw():
            self.redraw_graph()
            if self.on_deselect_callback:
                self.on_deselect_callback()

        self.after(80, delayed_redraw)

    def center_graph(self):
        """Центрирование графа с плавной анимацией"""
        if not self.vertex_positions:
            return

        target_offset_x = 0
        target_offset_y = 0
        target_scale = 1.0

        old_offset_x = self.offset_x
        old_offset_y = self.offset_y
        old_scale = self.scale

        steps = 10
        current_step = 0

        def center_step():
            nonlocal current_step
            if current_step >= steps:
                self.offset_x = target_offset_x
                self.offset_y = target_offset_y
                self.scale = target_scale
                self.redraw_graph()
                return

            progress = current_step / steps
            ease_progress = progress * progress  # Квадратичный easing

            self.offset_x = old_offset_x + (target_offset_x - old_offset_x) * ease_progress
            self.offset_y = old_offset_y + (target_offset_y - old_offset_y) * ease_progress
            self.scale = old_scale + (target_scale - old_scale) * ease_progress

            self.redraw_graph()

            current_step += 1
            anim_id = self.after(40, center_step)
            self.active_animations.append(anim_id)

        center_step()

    def stop_all_animations(self):
        """Останавливает все активные анимации"""
        for anim_id in self.active_animations:
            self.after_cancel(anim_id)
        self.active_animations.clear()

        for glow_id, anim_id in list(self.glow_effects.items()):
            if anim_id:
                self.after_cancel(anim_id)
            self.delete(glow_id)
        self.glow_effects.clear()

    def get_vertex_degree(self, vertex):
        """Степень вершины"""
        degree = 0
        for edge in self.edges:
            if edge['source'] == vertex or edge['target'] == vertex:
                degree += 1
        return degree

    def get_vertex_neighbors(self, vertex):
        """Соседи вершины"""
        neighbors = []
        for edge in self.edges:
            if edge['source'] == vertex:
                neighbors.append(edge['target'])
            elif edge['target'] == vertex:
                neighbors.append(edge['source'])
        return neighbors

    def is_directed(self):
        """Проверяет, является ли граф направленным"""
        if hasattr(self.graph, 'properties') and hasattr(self.graph.properties, 'directed'):
            return self.graph.properties.directed
        return False


# Остальной код GraphBrowser и GraphVisualizerApp остается БЕЗ ИЗМЕНЕНИЙ

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
        canvas = tk.Canvas(main_container, bg=COLORS['bg_main'])
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
                                  height=6,
                                  bg='white',
                                  relief='flat')
        self.listbox.pack(side='left', fill='both', expand=True)

        listbox_scrollbar = ttk.Scrollbar(self.listbox_frame,
                                          orient='vertical',
                                          command=self.listbox.yview)
        listbox_scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=listbox_scrollbar.set)

        # Кнопка загрузки
        button_frame = tk.Frame(self.scrollable_frame, bg=COLORS['bg_main'])
        button_frame.pack(pady=10, padx=10, fill='x')

        load_btn = StyledButton(button_frame, text="Загрузить выбранный граф",
                                command=self.load_selected)
        load_btn.pack()

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
        self.canvas = tk.Canvas(self, bg=COLORS['bg_main'], highlightthickness=0)
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
        self.root.configure(bg=COLORS['bg_main'])

        self.graph = None
        self.explorer = None

        self.create_widgets()
        self.load_recent_file()

    def create_widgets(self):
        """Создает все виджеты интерфейса"""
        # Главный контейнер с цветом фона
        main_container = tk.Frame(self.root, bg=COLORS['bg_main'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Левая панель - Canvas для графа
        left_frame = tk.Frame(main_container, bg=COLORS['bg_main'], width=1200)
        left_frame.pack(side='left', fill='both', expand=True)
        left_frame.pack_propagate(False)

        # Рамка для Canvas
        canvas_frame = tk.Frame(left_frame, bg=COLORS['border'], bd=2, relief='solid')
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Canvas для отрисовки графа
        self.canvas = GraphCanvas(
            canvas_frame,
            on_vertex_selected=self.on_vertex_selected,
            on_edge_selected=self.on_edge_selected,
            on_deselect=self.on_deselect,
            width=1190,
            height=690
        )
        self.canvas.pack(fill='both', expand=True, padx=1, pady=1)

        # Правая панель - управление с прокруткой
        right_frame = ScrollableFrame(main_container, width=350)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)

        self.create_control_buttons(right_frame.scrollable_frame)
        self.create_graph_info_panel(right_frame.scrollable_frame)
        self.create_graph_browser(right_frame.scrollable_frame)
        self.create_selection_info_panel(right_frame.scrollable_frame)

    def create_control_buttons(self, parent):
        """Создает кнопки управления"""
        button_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        button_frame.pack(fill='x', padx=10, pady=10)

        # Заголовок панели управления
        title_label = tk.Label(button_frame, text="Управление", 
                              font=('Arial', 12, 'bold'),
                              bg=COLORS['bg_main'],
                              fg=COLORS['text'])
        title_label.pack(pady=(0, 10))

        buttons = [
            ("Открыть файл графа", self.open_graph_file),
            ("Открыть ZIP архив", self.open_zip_archive),
            ("Центрировать граф", self.center_graph),
            ("Выход", self.root.quit)
        ]

        for text, command in buttons:
            btn = StyledButton(button_frame, text=text, command=command, 
                              width=220, height=45)
            btn.pack(pady=8)

    def create_graph_info_panel(self, parent):
        """Создает панель информации о графе"""
        # Рамка с заголовком
        info_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        info_frame.pack(fill='x', padx=10, pady=10)

        # Заголовок
        title_frame = tk.Frame(info_frame, bg=COLORS['border'], height=30)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="Информация о графе", 
                              font=('Arial', 11, 'bold'),
                              bg=COLORS['border'],
                              fg=COLORS['text'])
        title_label.pack(pady=5)

        # Текстовое поле
        self.graph_info_text = scrolledtext.ScrolledText(info_frame,
                                                         height=10,
                                                         font=('Arial', 9),
                                                         state='disabled',
                                                         bg='white',
                                                         relief='flat',
                                                         bd=1)
        self.graph_info_text.pack(fill='both', expand=True)

    def create_graph_browser(self, parent):
        """Создает браузер графов для ZIP-архивов"""
        self.browser_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        self.browser_frame.pack_forget()  # Скрываем по умолчанию

        # Заголовок
        title_frame = tk.Frame(self.browser_frame, bg=COLORS['border'], height=30)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="Архив графов", 
                              font=('Arial', 11, 'bold'),
                              bg=COLORS['border'],
                              fg=COLORS['text'])
        title_label.pack(pady=5)

        self.browser = GraphBrowser(self.browser_frame)
        self.browser.pack(fill='both', expand=True, padx=5, pady=5)

        self.browser.listbox.bind('<<ListboxSelect>>', self.on_graph_selected_in_browser)

    def create_selection_info_panel(self, parent):
        """Создает панель информации о выбранном элементе"""
        # Рамка с заголовком
        selection_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        selection_frame.pack(fill='x', padx=10, pady=10)

        # Заголовок
        title_frame = tk.Frame(selection_frame, bg=COLORS['border'], height=30)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="Выбранный элемент", 
                              font=('Arial', 11, 'bold'),
                              bg=COLORS['border'],
                              fg=COLORS['text'])
        title_label.pack(pady=5)

        self.selection_info_text = scrolledtext.ScrolledText(selection_frame,
                                                             height=6,
                                                             font=('Arial', 9),
                                                             state='disabled',
                                                             bg='white',
                                                             relief='flat',
                                                             bd=1)
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
