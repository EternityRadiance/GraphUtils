@echo off
chcp 65001 >nul
echo ========================================
echo    Graph Visualizer - Запуск
echo ========================================
echo.

:: Проверка Python
python --version >nul 2>nul
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo.
    pause
    exit /b 1
)

:: Проверка основного файла
if not exist "GraphVisualizerApp.py" (
    echo ОШИБКА: Файл GraphVisualizerApp.py не найден!
    echo.
    pause
    exit /b 1
)

:: Проверка зависимостей
echo Проверка зависимостей...
python -c "import networkx; import matplotlib; print('✓ Все зависимости установлены')" 2>nul
if errorlevel 1 (
    echo.
    echo ВНИМАНИЕ: Некоторые зависимости отсутствуют!
    echo.
    set /p choice="Хотите установить зависимости? (Y/N): "
    if /i "%choice%"=="Y" (
        call install.bat
    ) else (
        echo Запуск невозможен без зависимостей.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Запуск программы...
echo ========================================
python GraphVisualizerApp.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo ОШИБКА: Программа завершилась с ошибкой
    echo ========================================
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Программа завершена
echo ========================================
pause