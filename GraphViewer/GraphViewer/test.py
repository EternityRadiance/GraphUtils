import tkinter as tk
from tkinter import filedialog
import os
from explorer import GraphExplorer
from graph_drawer import GraphDrawer

def select_file():
    """Открывает диалог выбора файла"""
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    # Настраиваем диалог
    filetypes = [
        ("ZIP архивы", "*.zip"),
        ("JSON файлы", "*.json"),
        ("Все файлы", "*.*")
    ]
    
    # Открываем диалог выбора файла
    file_path = filedialog.askopenfilename(
        title="Выберите файл с графом",
        filetypes=filetypes,
        initialdir=os.getcwd()  # Начинаем с текущей директории
    )
    
    root.destroy()
    
    if not file_path:
        print("Файл не выбран")
        return None
    
    return file_path

def test_graph():
    """Простая проверка загрузки графа"""
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ ЗАГРУЗКИ ГРАФА")
    print("=" * 50)
    
    # Выбираем файл
    file_path = select_file()
    
    if not file_path:
        return
    
    print(f"\nВыбран файл: {file_path}")
    
    # Создаем explorer
    explorer = GraphExplorer(file_path)
    drawer = GraphDrawer()
    
    # Получаем список файлов
    files = explorer.list_files()
    json_files = [f for f in files if f.endswith('.json')]
    
    print(f"\nНайдено файлов в источнике: {len(files)}")
    print(f"JSON файлов (графов): {len(json_files)}")
    
    if json_files:
        print("\nСписок графов:")
        for i, filename in enumerate(json_files[:10], 1):  # Показ первых 10 файлов
            print(f"  {i}. {filename}")
        
        if len(json_files) > 10:
            print(f"  ... и еще {len(json_files) - 10}")
        
        # Загрузка
        first_file = json_files[0]
        print(f"\nЗагружаем первый граф: {first_file}")
        
        graph = explorer.read_graph(first_file)
        
        if graph:
            print("\n+ Граф успешно загружен!")
            print(f"\nИнформация о графе:")
            print(f"  Автор: {graph.author}")
            print(f"  Вершин: {graph.vertices}")
            print(f"  Ребер: {graph.edges}")
            print(f"  Размер: {graph.size}")
            print(f"\nСвойства:")
            
            props = graph.properties.to_dict()
            for prop_name, prop_value in props.items():
                status = "+" if prop_value else "-"
                print(f"  {status} {prop_name}")
            
            # Отрисовываем
            print("\nОтрисовываю граф...")
            drawer.draw(graph)
            
        else:
            print("-\n Не удалось загрузить граф")
    else:
        print("-\n В выбранном файле/архиве нет JSON файлов графов")

if __name__ == "__main__":
    test_graph()