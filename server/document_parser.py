from docx import Document
from io import BytesIO


async def read_docx(file) -> list:
    """Читает заголовки из DOCX файла"""
    try:
        # Читаем файл
        file_content = await file.read()

        # Парсим DOCX
        doc = Document(BytesIO(file_content))

        sections = []

        # Ищем заголовки
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Если абзац не пустой
                text = paragraph.text.strip()
                # Если это похоже на заголовок (короткий или стиль Heading)
                if len(text) < 100 or paragraph.style.name.startswith('Heading'):
                    sections.append(text)

        return sections[:10]  # Возвращаем первые 10 найденных разделов

    except Exception as e:
        raise Exception(f"Ошибка чтения файла: {str(e)}")