from app.CombinedFrontend import run_combined_app

if __name__ == "__main__":
    try:
        run_combined_app()
    except KeyboardInterrupt:
        print("\nПриложение завершено по запросу пользователя")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        raise