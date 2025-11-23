from .GraphService import GraphService
from .DataTypes import GraphRequest, GraphTags, GraphSize


def main():
    # Инициализация сервиса
    graph_service = GraphService()

    # Загрузка meta файла
    if not graph_service.download_meta():
        print("Не удалось загрузить meta файл")
        return

    # Пример 1: Поиск всех графов от конкретного автора
    print("=== Поиск графов Румянцева Александра ===")
    request1 = GraphRequest(author="Румянцев Александр")
    results1 = graph_service.search(request1)
    print(f"Найдено графов: {len(results1)}")
    for graph in results1[:5]:  # Покажем первые 5
        print(f"  - {graph}")

    # Пример 2: Поиск по размеру и тегам
    print("\n=== Поиск маленьких связных графов ===")
    tags = GraphTags(connected=True)
    request2 = GraphRequest(size=GraphSize.SMALL, tags=tags)
    results2 = graph_service.search(request2)
    print(f"Найдено графов: {len(results2)}")

    # Пример 3: Нестрогий поиск по автору
    print("\n=== Нестрогий поиск по автору 'Артем' ===")
    request3 = GraphRequest(author="Артем", strict_search=False)
    results3 = graph_service.search(request3)
    print(f"Найдено графов: {len(results3)}")

    # Пример 4: Комплексный поиск
    print("\n=== Комплексный поиск: направленные взвешенные графы ===")
    complex_tags = GraphTags(directed=True, weighted=True)
    request4 = GraphRequest(tags=complex_tags)
    results4 = graph_service.search(request4)
    print(f"Найдено графов: {len(results4)}")

    # Пример скачивания (раскомментируйте для тестирования)
    if results1:
        print("\n=== Скачивание первых 3 графов ===")
        zip_path = graph_service.download_zip(results1[:3])
        print(f"Файл сохранен: {zip_path}")


if __name__ == "__main__":
    main()
