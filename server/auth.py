from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
import jwt
import time
import hashlib
from database.models import User, get_db
from config import settings


# Простое хеширование паролей
def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_token(username: str) -> str:
    payload = {
        "username": username,
        "exp": time.time() + settings.JWT_EXPIRE_MINUTES * 60
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def check_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Неверный токен")


async def get_current_user(
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Нужен заголовок Authorization")

    token = authorization.replace("Bearer ", "")
    payload = check_token(token)

    user = db.query(User).filter(User.username == payload["username"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


# Функция регистрации нового пользователя
def register_user(db: Session, username: str, password: str, email: str = None, full_name: str = None):
    # Проверяем, нет ли уже пользователя с таким именем
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    # Проверяем email, если указан
    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    # Валидация пароля
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Пароль должен содержать минимум 6 символов")

    # Создаем нового пользователя
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# Создаем только админа при первом запуске
def create_initial_admin(db: Session):
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Администратор"
        )
        db.add(admin_user)
        db.commit()