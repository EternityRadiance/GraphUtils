@echo off
chcp 65001 >nul
echo ========================================
echo    Graph Visualizer - Установка
echo ========================================
echo.

:: Проверка Python
python --version >nul 2>nul
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.8+ с python.org
    echo.
    pause
    exit /b 1
)

:: Показать версию Python
for /f "tokens=*" %%i in ('python --version') do set python_ver=%%i
echo %python_ver%

echo.
echo Установка зависимостей...

:: Обновление pip
python -m pip install --upgrade pip

:: Установка зависимостей
echo.
echo Установка networkx...
python -m pip install networkx

echo.
echo Установка matplotlib...
python -m pip install matplotlib

echo.
echo ========================================
echo    Установка завершена успешно!
echo ========================================
echo.
echo Для запуска программы выполните:
echo    python GraphVisualizerApp.py
echo или
echo    run.bat
echo.
pause