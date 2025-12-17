import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

try:
    from ai_checker import SimpleOllamaChecker

    AI_AVAILABLE = True
    print("ИИ-модуль загружен")
except ImportError as e:
    AI_AVAILABLE = False
    print(f"ИИ-модуль не загружен: {e}")


def normalize_section_name(text: str) -> str:
    """Нормализует название раздела для сравнения"""
    if not text:
        return ""

    # Приводим к нижнему регистру
    text = text.lower().strip()

    # Убираем знаки препинания
    text = re.sub(r'[^\w\s]', ' ', text)

    # Заменяем множественные пробелы на один
    text = re.sub(r'\s+', ' ', text)

    # Убираем стоп-слова
    stop_words = ['глава', 'раздел', 'часть', 'параграф', 'пункт', 'заголовок', 'раздел']
    words = text.split()
    filtered_words = [w for w in words if w not in stop_words]

    return ' '.join(filtered_words).strip()


def compare_sections(found_sections: list, template_sections: list) -> dict:
    """Сравнивает найденные разделы с шаблоном с использованием ИИ"""

    # ОЧИСТКА НАЙДЕННЫХ РАЗДЕЛОВ ПЕРЕД ПРОВЕРКОЙ
    cleaned_found = []
    for section in found_sections:
        # Убираем префиксы типа "Заголовок: ", "Раздел: "
        clean = re.sub(r'^(Заголовок:|Раздел:|Раздел\s*\d+:|Глава\s*\d+:)\s*', '', str(section), flags=re.IGNORECASE)
        clean = clean.strip()

        # Убираем номера в начале "1. ", "2) ", "I. ", "1.1 "
        clean = re.sub(r'^\s*[\dIVX]+([\.\)]|\d+\.)*\s*', '', clean)
        clean = clean.strip()

        # Убираем символы форматирования
        clean = re.sub(r'[*_\-]{2,}', '', clean)
        clean = clean.strip()

        if clean and len(clean) > 2 and len(clean) < 200:  # Не слишком длинные
            cleaned_found.append(clean)

    # Если очистили успешно, используем очищенные
    if cleaned_found:
        found_sections = cleaned_found
        print(f"После очистки найдено {len(found_sections)} разделов:")
        for i, section in enumerate(found_sections, 1):
            print(f"  {i}. '{section}'")

    # Словарь синонимов для базовой проверки
    SECTION_SYNONYMS = {
        "титульный лист": ["титульный", "министерство", "университет", "кафедра",
                           "лабораторная работа", "факультет", "институт", "название", "тема"],
        "введение": ["введение", "цель работы", "задание", "цель", "вступление",
                     "постановка задачи", "актуальность"],
        "теория": ["теория", "теоретическая часть", "расчет", "методика",
                   "теоретические основы", "литературный обзор", "теоретический анализ",
                   "теоретический", "теоретические"],
        "практика": ["практика", "практическая часть", "эксперимент", "результаты",
                     "исследование", "опыты", "анализ", "экспериментальная часть",
                     "практическое", "реализация", "ход работы"],
        "заключение": ["заключение", "вывод", "выводы", "итоги", "результаты",
                       "заключительная часть", "общие выводы", "заключительные"],
        "литература": ["литература", "библиография", "источники", "список литературы",
                       "использованная литература", "список источников", "список использованных"],
        "содержание": ["оглавление", "содержание", "план", "структура", "план работы"],
        "библиография": ["библиография", "список литературы", "литература",
                         "источники", "список использованных источников"],
        "основная часть": ["основная часть", "теория", "практика", "разработка",
                           "анализ", "исследовательская часть", "экспериментальная часть"]
    }

    found_matches = []
    missing = []
    ai_synonyms = []
    spelling_errors = []

    # Инициализируем ИИ-проверку
    ai_checker = None
    if AI_AVAILABLE:
        try:
            ai_checker = SimpleOllamaChecker()
            if ai_checker.is_available:
                print(f"ИИ-проверка активна, модель: {ai_checker.model}")
            else:
                print("ИИ-проверка неактивна")
                ai_checker = None
        except Exception as e:
            print(f"Ошибка при инициализации ИИ: {e}")
            ai_checker = None
    else:
        print("ИИ-модуль отключен")

    # Проверяем орфографию если ИИ доступен
    if ai_checker and ai_checker.is_available and found_sections:
        try:
            # Объединяем весь текст для проверки орфографии
            all_text = " ".join(found_sections)
            if len(all_text) > 20:
                print("Проверка орфографии...")
                spelling_result = ai_checker.check_spelling(all_text)
                if spelling_result["has_errors"]:
                    spelling_errors = spelling_result["corrections"]
                    print(f"Найдено орфографических ошибок: {len(spelling_errors)}")
                else:
                    print("Орфографических ошибок не найдено")
        except Exception as e:
            print(f"Ошибка при проверке орфографии: {e}")

    # Проверяем каждый требуемый раздел
    for required in template_sections:
        required_normalized = normalize_section_name(required)
        required_lower = required.lower()
        found = False
        matched_section = None
        ai_match = False
        ai_explanation = ""
        match_method = ""

        # Сначала ищем среди найденных разделов
        for found_section in found_sections:
            if not found_section or len(found_section.strip()) < 2:
                continue

            found_normalized = normalize_section_name(found_section)
            found_lower = found_section.lower()

            # 1. Прямое совпадение (самое точное)
            if required_normalized == found_normalized or required_lower == found_lower:
                found = True
                matched_section = found_section
                match_method = "прямое совпадение"
                break

            # 2. Частичное совпадение по нормализованным версиям
            if (required_normalized in found_normalized or
                    found_normalized in required_normalized):
                found = True
                matched_section = found_section
                match_method = "частичное совпадение"
                break

            # 3. Проверка по словарю синонимов
            if required_lower in SECTION_SYNONYMS:
                for synonym in SECTION_SYNONYMS[required_lower]:
                    synonym_normalized = normalize_section_name(synonym)
                    if (synonym in found_lower or
                            synonym_normalized in found_normalized or
                            found_normalized in synonym_normalized):
                        found = True
                        matched_section = found_section
                        match_method = f"синоним: {synonym}"
                        break
                if found:
                    break

        # 4. Проверка через ИИ если не нашли прямыми методами
        if not found and ai_checker and ai_checker.is_available:
            print(f"Проверка через ИИ: '{required}'")

            best_match = None
            best_explanation = ""

            # Проверяем каждый найденный раздел через ИИ
            for found_section in found_sections:
                if not found_section or len(found_section) < 3:
                    continue

                try:
                    result_ai = ai_checker.check_synonyms(found_section, required)
                    if result_ai.get("is_synonym", False):
                        found = True
                        best_match = found_section
                        best_explanation = result_ai.get("explanation", "")
                        ai_match = True
                        ai_explanation = best_explanation
                        match_method = "ИИ-синоним"
                        break
                except Exception as e:
                    print(f"Ошибка ИИ-проверки: {e}")
                    continue

            if found and best_match:
                ai_synonyms.append({
                    "required": required,
                    "found": best_match,
                    "explanation": best_explanation,
                    "method": match_method
                })
                matched_section = best_match

        # ЗАПИСЫВАЕМ РЕЗУЛЬТАТ (ИЗМЕНЕННАЯ ЧАСТЬ)
        if found and matched_section:
            if ai_match:
                # Для ИИ-находок показываем соответствие в формате "Требуемый раздел (найден как: Фактический)"
                found_matches.append(f"{required} (найден как: {matched_section})")
            else:
                # Для прямых совпадений показываем просто раздел
                found_matches.append(matched_section)
            print(f"✓ Найден раздел '{required}' → '{matched_section}' ({match_method})")
        else:
            missing.append(required)
            print(f"✗ Отсутствует раздел: '{required}'")

    # Расчет оценки
    total = len(template_sections)
    found_count = len(found_matches)
    score = round((found_count / total * 100), 1) if total > 0 else 0

    # Определение статуса
    if score >= 80:
        status = "Отлично"
    elif score >= 60:
        status = "Хорошо"
    elif score >= 40:
        status = "Удовлетворительно"
    else:
        status = "Требует доработки"

    # Формируем результат
    result = {
        "найдено_разделов": found_matches,
        "отсутствуют": missing,
        "оценка": score,
        "статус": status,
        "совпадения_детально": f"Найдено {found_count} из {total} разделов"
    }

    # Добавляем результаты ИИ если есть
    if ai_synonyms:
        result["ai_synonyms"] = ai_synonyms
        print(f"ИИ нашел синонимы: {len(ai_synonyms)}")

    if spelling_errors:
        result["орфографические_ошибки"] = spelling_errors
        print(f"Найдено орфографических ошибок: {len(spelling_errors)}")

    # Отладочная информация
    print(f"Итоговый результат проверки:")
    print(f"  - Оценка: {score}%")
    print(f"  - Статус: {status}")
    print(f"  - Найдено разделов: {found_count}/{total}")
    print(f"  - Отсутствуют разделы: {len(missing)}")
    if ai_synonyms:
        print(f"  - ИИ синонимы: {len(ai_synonyms)}")
        for item in ai_synonyms:
            print(f"    * {item['required']} -> {item['found']}")
    if spelling_errors:
        print(f"  - Орф. ошибки: {len(spelling_errors)}")

    return result


# Шаблоны документов
TEMPLATES = {
    "лабораторная": [
        "Титульный лист",
        "Введение",
        "Теория",
        "Практика",
        "Заключение",
        "Литература"
    ],
    "курсовая": [
        "Титульный лист",
        "Содержание",
        "Введение",
        "Основная часть",
        "Заключение",
        "Библиография"
    ]
}