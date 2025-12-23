import networkx as nx
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any
from graph_models import Graph

class GraphDrawer:
    """
    Класс для визуализации графов с параметрами
    """
    
    def __init__(self):
        """Инициализация"""
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
    
    def create_networkx_graph(self, graph: Graph) -> nx.Graph:
        """
        Создание графа networkx из объекта Graph
        """
        # Выбирор типа графа на основе свойств
        if graph.properties.directed:
            if graph.properties.mixed:
                G = nx.MultiDiGraph()
            else:
                G = nx.DiGraph()
        else:
            if graph.properties.mixed:
                G = nx.MultiGraph()
            else:
                G = nx.Graph()
        
        # Добавление вершины
        for i in range(graph.vertices):
            G.add_node(i, label=str(i))
        
        # Добавление ребер с учетом весов
        for edge in graph.edges_list:
            source = edge['source']
            target = edge['target']
            
            if graph.properties.weighted:
                weight = edge.get('weight', 1.0)
                G.add_edge(source, target, weight=weight)
            else:
                G.add_edge(source, target)
        
        return G
    
    def draw(self, graph: Graph, save_path: Optional[str] = None):
        """
        Отрисовка графа
        """
        self.ax.clear()
        
        # Создание графа
        G = self.create_networkx_graph(graph)
        
        # Выбор layout в зависимости от свойств
        if graph.properties.tree:
            # Для деревьев 
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        elif graph.properties.planar or graph.vertices < 30:
            # Для планарных или маленьких графов
            pos = nx.planar_layout(G) if graph.properties.planar else nx.spring_layout(G, k=1)
        elif graph.properties.full:
            # Для полных графов
            pos = nx.circular_layout(G)
        else:
            # По умолчанию
            pos = nx.spring_layout(G, k=2/len(G)**0.5)
        
        # Определение цвета на основе свойств
        node_color = self._get_node_color(graph)
        edge_color = self._get_edge_color(graph)
        
        # Отриовка графа
        if graph.properties.directed:
            nx.draw_networkx_nodes(G, pos, ax=self.ax, 
                                 node_color=node_color, 
                                 edgecolors='black',
                                 node_size=400)
            nx.draw_networkx_edges(G, pos, ax=self.ax,
                                 edge_color=edge_color,
                                 arrows=True,
                                 arrowsize=25,
                                 width=2)
        else:
            nx.draw_networkx_nodes(G, pos, ax=self.ax,
                                 node_color=node_color,
                                 edgecolors='black',
                                 node_size=400)
            nx.draw_networkx_edges(G, pos, ax=self.ax,
                                 edge_color=edge_color,
                                 width=2)
        
        # Подписи вершин
        if graph.vertices <= 50:  # Не показывать для очень больших графов
            nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=9)
        
        # Заголовок
        self._add_detailed_title(graph)
        
        self.ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Сохранено: {save_path}")
        else:
            plt.show()
    
    def _get_node_color(self, graph: Graph) -> str:
        """Возвращает цвет узлов в зависимости от свойств"""
        if graph.properties.tree:
            return '#90EE90'  # Светло-зеленый для деревьев
        elif graph.properties.full:
            return '#FFB6C1'  # Светло-розовый для полных графов
        elif graph.properties.empty:
            return '#D3D3D3'  # Светло-серый для пустых графов
        elif graph.properties.planar:
            return '#ADD8E6'  # Светло-голубой для планарных
        elif graph.properties.double:
            return '#FFD700'  # Золотой для двудольных
        else:
            return '#FFA07A'  # Светло-лососевый по умолчанию
    
    def _get_edge_color(self, graph: Graph) -> str:
        """Возвращает цвет ребер в зависимости от свойств"""
        if graph.properties.weighted:
            return '#FF4500'  # Оранжево-красный для взвешенных
        elif graph.properties.mixed:
            return '#9400D3'  # Темно-фиолетовый для смешанных
        elif graph.properties.pseudo:
            return '#DC143C'  # Малиновый для псевдографов
        else:
            return '#2F4F4F'  # Темно-серый по умолчанию
    
    def _add_detailed_title(self, graph: Graph):
        """Добавляет заголовок со свойствами"""
        title_lines = [
            f"Граф: {graph.author}",
            f"Вершин: {graph.vertices}, Ребер: {graph.edges}, Размер: {graph.size}",
            "СВОЙСТВА:"
        ]
        
        # Активные свойства
        active_props = graph.get_active_properties()
        if active_props:
            title_lines.append("+ " + ", ".join(active_props))
        
        # Неактивные свойства
        all_props = graph.properties.to_dict()
        inactive_props = [prop for prop, value in all_props.items() if not value]
        if inactive_props:
            title_lines.append("- " + ", ".join(inactive_props))
        
        title = "\n".join(title_lines)
        self.ax.set_title(title, fontsize=10, pad=20, loc='left')
    
    def analyze_graph(self, graph: Graph) -> Dict[str, Any]:
        """
        Анализ графа и возврат дополнительной информации
        """
        G = self.create_networkx_graph(graph)
        
        analysis = {
            "filename": "graph_2.json",  # Будет передаваться извне
            "author": graph.author,
            "basic_info": {
                "vertices": graph.vertices,
                "edges": graph.edges,
                "size": graph.size
            },
            "declared_properties": graph.properties.to_dict(),
            "networkx_analysis": {}
        }
        
        # Анализ с помощью networkx
        try:
            # Проверка связности
            if graph.properties.directed:
                analysis["networkx_analysis"]["is_strongly_connected"] = nx.is_strongly_connected(G)
                analysis["networkx_analysis"]["is_weakly_connected"] = nx.is_weakly_connected(G)
            else:
                analysis["networkx_analysis"]["is_connected"] = nx.is_connected(G)
            
            # Проверка простоты графа
            analysis["networkx_analysis"]["is_simple"] = nx.is_simple(G)
            
            # Проверка двудольности (если double=True в свойствах)
            if graph.properties.double:
                try:
                    analysis["networkx_analysis"]["is_bipartite"] = nx.is_bipartite(G)
                except:
                    analysis["networkx_analysis"]["is_bipartite"] = "Cannot determine"
            
            # Проверка на дерево
            analysis["networkx_analysis"]["is_tree"] = nx.is_tree(G) if not graph.properties.directed else False
            
            # Степени вершин
            if len(G) > 0:
                degrees = dict(G.degree())
                analysis["networkx_analysis"]["degree_info"] = {
                    "min_degree": min(degrees.values()),
                    "max_degree": max(degrees.values()),
                    "avg_degree": sum(degrees.values()) / len(degrees)
                }
            
        except Exception as e:
            analysis["networkx_analysis"]["error"] = str(e)
        
        return analysis