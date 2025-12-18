import os
import json
from explorer import GraphExplorer
from graph_drawer import GraphDrawer

def main():
    # Путь к ZIP-архиву
    zip_path = "graphs_294_files.zip"
    
    if not os.path.exists(zip_path):
        print(f"Файл не найден: {zip_path}")
        return
    
    # Инициализация
    explorer = GraphExplorer(zip_path)
    drawer = GraphDrawer()
    
    # Получение списка файлов
    files = explorer.list_files()
    json_files = [f for f in files if f.endswith('.json')]
    
    print(f"Найдено {len(json_files)} файлов с графами")
    
    # Загрузка и анализ первого графа
    if json_files:
        first_file = json_files[0]
        print(f"\nЗагружаем: {first_file}")
        
        graph = explorer.read_graph(first_file)
        if graph:
            print("\n" + "="*60)
            print("ПОЛНАЯ ИНФОРМАЦИЯ О ГРАФЕ:")
            print("="*60)
            print(f"Автор: {graph.author}")
            print(f"Размер: {graph.size}")
            print(f"Вершин: {graph.vertices}")
            print(f"Ребер: {graph.edges}")
            
            print("\nВСЕ СВОЙСТВА ГРАФА:")
            print("-"*40)
            props_dict = graph.properties.to_dict()
            for prop_name, prop_value in props_dict.items():
                status = "+ ВКЛЮЧЕНО" if prop_value else "- ВЫКЛЮЧЕНО"
                print(f"{prop_name:15} -> {status}")
            
            print("\nАКТИВНЫЕ СВОЙСТВА:")
            active_props = graph.get_active_properties()
            if active_props:
                for prop in active_props:
                    print(f"  - {prop}")
            else:
                print("  (нет активных свойств)")
            
            # Анализируем граф
            print("\n" + "="*60)
            print("АНАЛИЗ NETWORKX:")
            print("="*60)
            analysis = drawer.analyze_graph(graph)
            
            for key, value in analysis["networkx_analysis"].items():
                if isinstance(value, dict):
                    print(f"\n{key}:")
                    for subkey, subvalue in value.items():
                        print(f"  {subkey}: {subvalue}")
                else:
                    print(f"{key}: {value}")
            
            # Отрисовываем граф
            print("\nОтрисовываю граф...")
            drawer.draw(graph)
            
        else:
            print("Не удалось загрузить граф")
    else:
        print("Нет JSON файлов")

if __name__ == "__main__":
    main()