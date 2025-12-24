from app.GraphFrontend import run_frontend
from app.ConsoleWidget import get_console

if __name__ == "__main__":
    try:
        run_frontend()
    except KeyboardInterrupt:
        console = get_console()
        if console:
            console.log_system("Приложение завершено по запросу пользователя")
        print("Приложение завершено.")
    except Exception as e:
        console = get_console()
        if console:
            console.log_error(f"Критическая ошибка: {e}")
        raise