from docx import Document
from io import BytesIO


async def read_docx(file) -> list:
    try:
        file_content = await file.read()
        doc = Document(BytesIO(file_content))

        sections = []

        # Собираем все значимые заголовки и параграфы
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue

            # Определяем уровень заголовка
            style_name = paragraph.style.name.lower()

            # Заголовки разных уровней
            if any(keyword in style_name for keyword in ['heading', 'title', 'header']):
                sections.append(f"Заголовок: {text}")

            # Нумерованные пункты (1., 2., 1.1, 2.1 и т.д.)
            elif text[:3].replace('.', '').isdigit() and len(text) > 10:
                sections.append(f"Раздел: {text}")

            # Короткие важные строки (скорее всего заголовки)
            elif len(text) < 150 and any(keyword in text.lower() for keyword in
                                         ['цель', 'задание', 'ход работы', 'вывод',
                                          'введение', 'заключение', 'литература']):
                sections.append(f"Раздел: {text}")

        # Если мало найдено, берем первые 10 непустых параграфов
        if len(sections) < 5:
            sections = [p.text.strip() for p in doc.paragraphs if p.text.strip()][:15]

        return sections

    except Exception as e:
        raise Exception(f"Ошибка чтения файла: {str(e)}")