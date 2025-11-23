import json
import requests
import os
import zipfile
from typing import List, Dict, Any, Optional

from .DataTypes import GraphRequest, GraphTags, GraphSize
from .config import REPO_URL, BASE_SAVE_PATH, META_FILE_URL


class GraphService:
    def __init__(self):
        self.meta_data: Dict[str, Any] = {}
        self.loaded = False

    def download_meta(self) -> bool:
        """
        Загружает meta-файл при запуске приложения в память
        Возвращает True при успешной загрузке, False при ошибке
        """
        try:
            print(f"Загружаем meta файл из: {META_FILE_URL}")
            response = requests.get(META_FILE_URL)
            response.raise_for_status()

            # Выводим первые 500 символов ответа для диагностики
            content_preview = response.text[:500]
            print(f"Полученный ответ (первые 500 символов): {content_preview}")

            # Пробуем распарсить JSON
            self.meta_data = response.json()
            self.loaded = True
            print(f"Meta файл успешно загружен. Загружено {len(self.meta_data)} графов")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке meta файла: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Ошибка при парсинге meta файла: {e}")
            # Выводим больше информации об ошибке
            print(f"Позиция ошибки: строка {e.lineno}, колонка {e.colno}")
            print(f"Контекст ошибки: {e.doc}")
            return False
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return False

    def search(self, request: GraphRequest) -> List[str]:
        """
        Ищет внутри мета файла по GraphRequest
        Возвращает список имён графов для скачивания
        """
        if not self.loaded:
            print("Meta файл не загружен. Сначала вызовите download_meta()")
            return []

        if request.is_empty():
            print("Пустой запрос. Возвращаем все графы.")
            return list(self.meta_data.keys())

        matching_graphs = []

        for graph_name, graph_data in self.meta_data.items():
            if self._matches_request(graph_data, request):
                matching_graphs.append(graph_name)

        return matching_graphs

    def _matches_request(self, graph_data: Dict[str, Any], request: GraphRequest) -> bool:
        """Проверяет, соответствует ли граф критериям запроса"""
        # Проверка автора
        if request.author is not None:
            if request.strict_search:
                if graph_data.get('author') != request.author:
                    return False
            else:
                author = graph_data.get('author', '')
                if author and request.author.lower() not in author.lower():
                    return False

        # Проверка размера
        if request.size is not None:
            graph_size = graph_data.get('size')
            if graph_size != request.size.value:
                return False

        # Проверка тегов
        if request.tags is not None:
            graph_properties = graph_data.get('properties', {})
            if not self._matches_properties(graph_properties, request.tags, request.strict_search):
                return False

        return True

    def _matches_properties(self, graph_properties: Dict[str, Any], request_tags: GraphTags, strict: bool) -> bool:
        """Проверяет соответствие свойств графа тегам запроса"""
        for attr_name in dir(request_tags):
            if attr_name.startswith('_') or attr_name == 'from_dict':
                continue

            request_value = getattr(request_tags, attr_name)
            if request_value is not None:
                graph_value = graph_properties.get(attr_name)

                if strict:
                    # Строгий поиск: значения должны точно совпадать
                    if request_value != graph_value:
                        return False
                else:
                    # Нестрогий поиск: если в графе есть значение, оно должно совпадать
                    if graph_value is not None and request_value != graph_value:
                        return False

        return True

    def download_zip(self, graph_names: List[str], save_path: Optional[str] = None) -> str:
        """
        Скачивает графы и создает zip архив
        Возвращает путь к созданному zip файлу
        """
        if not graph_names:
            raise ValueError("Список графов для скачивания пуст")

        if save_path is None:
            save_path = BASE_SAVE_PATH

        # Создаем директорию для сохранения, если её нет
        os.makedirs(save_path, exist_ok=True)

        # Временная директория для скачанных файлов
        temp_dir = os.path.join(save_path, "temp_graphs")
        os.makedirs(temp_dir, exist_ok=True)

        downloaded_files = []

        try:
            # Скачиваем каждый граф
            for graph_name in graph_names:
                graph_filename = f"{graph_name}.json"
                graph_url = f"{REPO_URL}/{graph_filename}"

                try:
                    response = requests.get(graph_url)
                    response.raise_for_status()

                    file_path = os.path.join(temp_dir, graph_filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(response.json(), f, ensure_ascii=False, indent=2)

                    downloaded_files.append(file_path)
                    print(f"Успешно скачан: {graph_filename}")

                except requests.exceptions.RequestException as e:
                    print(f"Ошибка при скачивании {graph_filename}: {e}")

            # Создаем zip архив
            zip_filename = f"graphs_{len(graph_names)}_files.zip"
            zip_path = os.path.join(save_path, zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in downloaded_files:
                    zipf.write(file_path, os.path.basename(file_path))

            print(f"Zip архив создан: {zip_path}")
            return zip_path

        finally:
            # Очищаем временные файлы
            for file_path in downloaded_files:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass

    def get_graph_info(self, graph_name: str) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о конкретном графе"""
        return self.meta_data.get(graph_name)

    def get_all_authors(self) -> List[str]:
        """Возвращает список всех авторов"""
        if not self.loaded:
            return []
        authors = set()
        for graph_data in self.meta_data.values():
            author = graph_data.get('author')
            if author:
                authors.add(author)
        return sorted(list(authors))

    def load_meta_from_file(self, file_path: str) -> bool:
        """
        Альтернативный метод: загрузка meta файла из локального файла
        Полезно для тестирования
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.meta_data = json.load(f)
            self.loaded = True
            print(f"Meta файл успешно загружен из {file_path}. Загружено {len(self.meta_data)} графов")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке meta файла из {file_path}: {e}")
            return False
