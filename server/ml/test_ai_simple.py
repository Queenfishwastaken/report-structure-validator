# test_ai_simple.py
import sys
import os

# Добавляем текущую директорию
sys.path.append(os.path.dirname(__file__))

print("=== Простой тест ИИ ===")
print("Текущая директория:", os.getcwd())
print("Файлы:", os.listdir('.'))

try:
    # Импортируем модуль
    import ai_checker

    print("✅ Модуль импортирован")

    # Проверяем класс
    if hasattr(ai_checker, 'SimpleOllamaChecker'):
        print("✅ Класс найден")

        # Создаем экземпляр
        checker = ai_checker.SimpleOllamaChecker()
        print(f"✅ Экземпляр создан")
        print(f"Доступность: {checker.is_available}")
        print(f"Модель: {checker.model}")

        # Быстрый тест
        if checker.is_available:
            print("\n🔤 Тест синонимов:")
            result = checker.check_synonyms("Введение", "Вступление")
            print(f"Результат: {result}")

            print("\n🔍 Тест орфографии:")
            result = checker.check_spelling("тествовый текст")
            print(f"Результат: {result}")
        else:
            print("❌ Ollama недоступна")

    else:
        print("❌ Класс не найден")
        print("Что есть в модуле:", dir(ai_checker))

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback

    traceback.print_exc()
except Exception as e:
    print(f"❌ Другая ошибка: {e}")
    import traceback

    traceback.print_exc()