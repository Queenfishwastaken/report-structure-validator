import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """Очищает текст от лишних пробелов и символов"""
    return re.sub(r'\s+', ' ', text).strip()


def find_similar_sections(text: str, target_sections: List[str]) -> Dict[str, bool]:
    """Находит похожие разделы в тексте"""
    results = {}
    text_lower = text.lower()

    for section in target_sections:
        section_lower = section.lower()
        # Простой поиск по вхождению
        if section_lower in text_lower:
            results[section] = True
        else:
            # Можно добавить более сложную логику сравнения
            results[section] = False

    return results