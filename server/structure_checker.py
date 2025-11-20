def compare_sections(found_sections: list, template_sections: list) -> dict:

    # Словарь синонимов и похожих разделов
    SECTION_SYNONYMS = {
        "титульный лист": ["титульный", "министерство", "университет", "кафедра", "лабораторная работа"],
        "введение": ["введение", "цель работы", "задание", "цель"],
        "теория": ["теория", "ход работы", "расчет", "методика", "маски"],
        "практика": ["практика", "результаты", "эксперимент", "реализация"],
        "заключение": ["заключение", "вывод", "итоги", "результаты"],
        "литература": ["литература", "библиография", "источники", "список литературы"]
    }

    found_matches = []
    missing = []

    # Проверяем каждый требуемый раздел
    for required in template_sections:
        required_lower = required.lower()
        found = False

        # Ищем прямые совпадения
        for found_section in found_sections:
            found_lower = found_section.lower()

            # Прямое вхождение
            if required_lower in found_lower:
                found = True
                found_matches.append(found_section)
                break

            # Проверяем синонимы
            if required_lower in SECTION_SYNONYMS:
                for synonym in SECTION_SYNONYMS[required_lower]:
                    if synonym in found_lower:
                        found = True
                        found_matches.append(f"{required} (найден как: '{found_section}')")
                        break
                if found:
                    break

        if not found:
            missing.append(required)

    # Считаем оценку (более мягкая система)
    total = len(template_sections)
    found_count = total - len(missing)
    score = round(found_count / total * 100, 1) if total > 0 else 0

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
        "найдено_разделов": found_matches,
        "отсутствуют": missing,
        "оценка": score,
        "статус": status,
        "совпадения_детально": f"Найдено {found_count} из {total} разделов"
    }


# Улучшенные шаблоны
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