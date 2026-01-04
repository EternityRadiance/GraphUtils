import os
import zipfile
import json
from typing import List, Optional, Dict, Any
from graph_models import Graph


class GraphExplorer:
    """
    Класс для работы с файлами в директориях и ZIP-архивах.
    """

    def __init__(self, path: str) -> None:
        """
        Инициализирует объект для работы с директорией или ZIP-архивом.

        Args:
            path: Путь к директории или ZIP-архиву
        """
        self.path = path

    def list_files(self) -> List[str]:
        """
        Возвращает список имён файлов в директории или ZIP-архиве.

        Returns:
            Список имён файлов (без директорий)
        """
        if self.path.endswith('.zip'):
            try:
                with zipfile.ZipFile(self.path, 'r') as zip_file:
                    file_names = []
                    for name in zip_file.namelist():
                        if not name.endswith('/'):
                            file_names.append(os.path.basename(name))
                    return file_names
            except Exception as e:
                print(f"Ошибка при чтении ZIP-архива: {e}")
                return []

        elif os.path.isdir(self.path):
            items = os.listdir(self.path)
            file_names = []
            for item in items:
                item_path = os.path.join(self.path, item)
                if os.path.isfile(item_path):
                    file_names.append(item)
            return file_names

        else:
            print(f"Путь '{self.path}' не является директорией или ZIP-файлом")
            return []

    def read_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Читает JSON-файл из директории или ZIP-архива.

        Args:
            filename: Имя JSON-файла для чтения

        Returns:
            Содержимое JSON-файла в виде словаря или None при ошибке
        """
        try:
            if self.path.endswith('.zip'):
                with zipfile.ZipFile(self.path, 'r') as zf:
                    for name in zf.namelist():
                        if os.path.basename(name) == filename:
                            with zf.open(name) as f:
                                return json.load(f)
                    return None

            elif os.path.isdir(self.path):
                file_path = os.path.join(self.path, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return None

            return None

        except Exception:
            return None

    def read_graph(self, filename: str) -> Optional[Graph]:
        """
        Читает и парсит граф в объект Graph со ВСЕМИ свойствами.

        Args:
            filename: Имя JSON-файла

        Returns:
            Объект Graph или None при ошибке
        """
        try:
            json_data = self.read_file(filename)
            if json_data is None:
                return None
            return Graph.from_json(json_data)
        except Exception as e:
            print(f"Ошибка при парсинге графа {filename}: {e}")
            return None

    def get_all_graphs(self) -> Dict[str, Graph]:
        """
        Загружает все графы со ВСЕМИ свойствами.

        Returns:
            Словарь {имя_файла: Graph}
        """
        graphs = {}
        files = self.list_files()

        for filename in files:
            if filename.endswith('.json'):
                graph = self.read_graph(filename)
                if graph:
                    graphs[filename] = graph

        return graphs