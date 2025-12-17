import requests
import re


class SimpleOllamaChecker:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "tinyllama:latest"
        self.is_available = self._check_availability()

    def _check_availability(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get('name') for m in models]

                # Ищем tinyllama
                for model_name in model_names:
                    if "tinyllama" in model_name.lower():
                        self.model = model_name
                        print(f"Используем модель: {self.model}")
                        return True

                return True
            return False
        except:
            return False

    def ask_ollama(self, question: str) -> str:
        data = {
            "model": self.model,
            "prompt": question,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.3
            }
        }

        try:
            response = requests.post(self.ollama_url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Ошибка: {response.status_code}"
        except Exception as e:
            return f"Не удалось подключиться к Ollama. Ошибка: {e}"

    def check_synonyms(self, student_word: str, template_word: str) -> dict:
        # Сначала проверяем базовые синонимы без ИИ
        basic_synonyms = {
            "практика": ["практическая", "эксперимент", "исследование", "реализация"],
            "литература": ["список", "источники", "библиография", "использованных"],
            "введение": ["введение"],
            "теория": ["теоретическая", "теоретический"],
            "заключение": ["заключительные", "выводы", "вывод"],
            "содержание": ["оглавление"],
            "титульный": ["титульный", "обложка"]
        }

        student_lower = student_word.lower()
        template_lower = template_word.lower()

        # Проверяем по базовым синонимам
        if template_lower in basic_synonyms:
            for synonym in basic_synonyms[template_lower]:
                if synonym in student_lower:
                    return {
                        "is_synonym": True,
                        "explanation": f"'{student_word}' содержит '{synonym}', что соответствует разделу '{template_word}'"
                    }

        question = f"""
        Требуется проверить, являются ли эти заголовки одинаковыми разделами в учебном отчете.

        Вопрос: Является ли заголовок студента: "{student_word}"
        таким же разделом как: "{template_word}"?

        Правила:
        1. Если заголовки означают один и тот же раздел отчета, ответь "ДА"
        2. Если заголовки разные, ответь "НЕТ"
        3. После ответа дай одно предложение объяснения

        Примеры:
        "Теоретическая часть" и "Теория" → ДА
        "Практическая реализация" и "Практика" → ДА
        "Список литературы" и "Литература" → ДА
        "ОГЛАВЛЕНИЕ" и "Содержание" → ДА
        "Введение" и "Заключение" → НЕТ

        Только ответ и краткое объяснение.
        """

        try:
            answer = self.ask_ollama(question)

            # Убираем лишний текст, ищем "ДА" или "НЕТ"
            clean_answer = answer.upper().strip()

            # Ищем ответ в первых 50 символах
            first_part = clean_answer[:50]

            if "ДА" in first_part:
                # Извлекаем объяснение
                explanation = ""
                if "НЕТ" not in first_part:  # Убедимся, что нет противоречий
                    # Пытаемся найти нормальное объяснение
                    lines = answer.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not ("ДА" in line.upper() or "НЕТ" in line.upper()):
                            if len(line) > 10:  # Берем только содержательные строки
                                explanation = line
                                break

                    if not explanation:
                        explanation = f"'{student_word}' соответствует разделу '{template_word}'"

                return {"is_synonym": True, "explanation": explanation}
            else:
                return {"is_synonym": False, "explanation": "Заголовки не соответствуют"}

        except Exception as e:
            # При ошибке ИИ, используем базовую проверку
            if any(word in student_lower for word in basic_synonyms.get(template_lower, [])):
                return {
                    "is_synonym": True,
                    "explanation": f"Базовое соответствие: '{student_word}' → '{template_word}'"
                }
            return {"is_synonym": False, "explanation": f"Ошибка ИИ: {str(e)}"}

    def check_spelling(self, text: str) -> dict:
        # Сначала проверяем базовые ошибки без ИИ
        basic_errors = {
            "првиет": "привет",
            "ошибками": "ошибками",
            "ошибок": "ошибок",
            "ошыбками": "ошибками",
            "ошыбки": "ошибки"
        }

        corrections = []

        # Проверяем текст на базовые ошибки
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if word in basic_errors:
                corrections.append({
                    "wrong": word,
                    "correct": basic_errors[word]
                })

        # Если нашли ошибки, возвращаем их
        if corrections:
            return {
                "has_errors": True,
                "corrections": corrections[:5]  # Ограничиваем количество
            }

        # Только если не нашли базовых ошибок, используем ИИ
        text_to_check = text[:300]  # Еще меньше текста для проверки

        question = f"""
        Найди орфографические ошибки в русском тексте.

        Текст: {text_to_check}

        Формат ответа:
        Если есть ошибки, напиши: слово->исправление
        Только слова и стрелки, ничего лишнего.
        Если нет ошибок, напиши: ОШИБОК НЕТ
        """

        try:
            answer = self.ask_ollama(question)

            if "ОШИБОК НЕТ" in answer.upper():
                return {"has_errors": False, "corrections": []}

            # Парсим ответ
            new_corrections = []
            lines = answer.split('\n')

            for line in lines:
                line = line.strip()
                if '->' in line:
                    parts = line.split('->')
                    if len(parts) == 2:
                        wrong = parts[0].strip()
                        correct = parts[1].strip()

                        # Проверяем, что слова разные и не слишком длинные
                        if (wrong and correct and
                                wrong != correct and
                                len(wrong) < 30 and
                                len(correct) < 30):
                            new_corrections.append({
                                "wrong": wrong,
                                "correct": correct
                            })

            # Объединяем с базовыми исправлениями
            all_corrections = corrections + new_corrections[:3]  # Ограничиваем
            return {
                "has_errors": len(all_corrections) > 0,
                "corrections": all_corrections
            }

        except Exception as e:
            return {
                "has_errors": len(corrections) > 0,
                "corrections": corrections
            }