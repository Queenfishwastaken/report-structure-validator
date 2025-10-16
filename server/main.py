from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from auth import check_user, create_token, get_user_from_header
from document_parser import read_docx
from structure_checker import compare_sections, TEMPLATES

app = FastAPI(title="Проверка структуры отчетов")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def главная():
    return {"сообщение": "Сервис проверки структуры отчетов работает!"}


@app.post("/вход")
async def вход(логин: str = Form(...), пароль: str = Form(...)):
    """Вход в систему"""
    if not check_user(логин, пароль):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    токен = create_token(логин)
    return {"токен": токен, "пользователь": логин}


@app.get("/шаблоны")
async def получить_шаблоны():
    """Показывает доступные шаблоны"""
    return {"шаблоны": TEMPLATES}


@app.post("/проверить")
async def проверить_документ(
        файл: UploadFile = File(..., description="DOCX файл"),
        шаблон: str = Form(..., description="Название шаблона"),
        пользователь: dict = Depends(get_user_from_header)
):
    """Основная функция - проверяет структуру документа"""

    # Проверяем шаблон
    if шаблон not in TEMPLATES:
        return {"ошибка": f"Шаблон '{шаблон}' не найден"}

    # Проверяем формат файла
    if not файл.filename.endswith('.docx'):
        return {"ошибка": "Нужен файл .docx"}

    try:
        найденные_разделы = await read_docx(файл)

        результат = compare_sections(найденные_разделы, TEMPLATES[шаблон])

        результат["файл"] = файл.filename
        результат["шаблон"] = шаблон
        результат["пользователь"] = пользователь["username"]

        return результат

    except Exception as e:
        return {"ошибка": f"Ошибка при проверке: {str(e)}"}


@app.get("/профиль")
async def мой_профиль(пользователь: dict = Depends(get_user_from_header)):
    """Показывает информацию о текущем пользователе"""
    return {
        "пользователь": пользователь["username"],
        "сообщение": f"Привет, {пользователь['username']}!"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)