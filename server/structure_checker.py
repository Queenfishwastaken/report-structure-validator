def compare_sections(found_sections: list, template_sections: list) -> dict:
    """Сравнивает найденные разделы с шаблоном"""

    missing = []

    # Проверяем каждый требуемый раздел
    for required in template_sections:
        found = False
        for found_section in found_sections:
            # Простое сравнение по вхождению слов
            if required.lower() in found_section.lower():
                found = True
                break
        if not found:
            missing.append(required)

    # Считаем оценку
    total = len(template_sections)
    score = round((total - len(missing)) / total * 100, 1)

    # Статус
    if score >= 80:
        status = "Отлично"
    elif score >= 60:
        status = "Хорошо"
    elif score >= 40:
        status = "Удовлетворительно"
    else:
        status = "Требует доработки"

    return {
        "найдено_разделов": found_sections,
        "отсутствуют": missing,
        "оценка": score,
        "статус": status
    }


# Шаблоны
TEMPLATES = {
    "лабораторная": ["Титульный лист", "Введение", "Теория", "Практика", "Заключение", "Литература"],
    "курсовая": ["Титульный лист", "Содержание", "Введение", "Основная часть", "Заключение", "Библиография"]
}