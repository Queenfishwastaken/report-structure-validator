from fastapi import HTTPException, Header
import jwt
import time

# Простые настройки
JWT_SECRET = "мой-секретный-ключ"
JWT_ALGORITHM = "HS256"

# Пользователи в памяти (для демо)
USERS = {
    "admin": "admin123",
    "student": "student123"
}


def check_user(username: str, password: str) -> bool:
    """Проверяет логин и пароль"""
    return USERS.get(username) == password


def create_token(username: str) -> str:
    """Создает JWT токен"""
    payload = {
        "username": username,
        "exp": time.time() + 3600  # На 1 час
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def check_token(token: str) -> dict:
    """Проверяет JWT токен"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Неверный токен")


async def get_user_from_header(authorization: str = Header(None)):
    """Достает пользователя из заголовка"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Нужен заголовок Authorization")

    token = authorization.replace("Bearer ", "")
    return check_token(token)