from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import json

from auth import authenticate_user, create_token, register_user, create_initial_admin
from document_parser import read_docx
from structure_checker import compare_sections, TEMPLATES
from database.models import get_db, create_tables, User, Report, ReportTemplate


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    db = next(get_db())
    create_initial_admin(db)
    print("Сервер запущен")
    yield


app = FastAPI(title="Report Structure Validator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/регистрация")
async def register(
        username: str = Form(...),
        password: str = Form(...),
        email: str = Form(None),
        full_name: str = Form(None),
        db: Session = Depends(get_db)
):
    user = register_user(db, username, password, email, full_name)
    token = create_token(username)

    return {
        "message": "User registered successfully",
        "token": token,
        "user": username,
        "user_id": user.id
    }

@app.post("/вход")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(username)

    return {
        "message": "Login successful",
        "token": token,
        "user": username,
        "user_id": user.id
    }

@app.get("/шаблоны")
async def get_templates(db: Session = Depends(get_db)):
    templates = db.query(ReportTemplate).all()
    return {
        "templates": {
            template.name: json.loads(template.sections)
            for template in templates
        }
    }

@app.post("/проверить")
async def check_document(
        file: UploadFile = File(..., description="DOCX file"),
        template: str = Form(..., description="Template name"),
        token: str = Form(None),  # Необязательный токен
        db: Session = Depends(get_db)
):

    if template not in TEMPLATES:
        return {"error": f"Template '{template}' not found"}

    if not file.filename.endswith('.docx'):
        return {"error": "DOCX file required"}

    try:
        found_sections = await read_docx(file)
        result = compare_sections(found_sections, TEMPLATES[template])

        user_id = 1
        username = "anonymous"

        if token:
            from auth import check_token
            try:
                payload = check_token(token)
                user = db.query(User).filter(User.username == payload["username"]).first()
                if user:
                    user_id = user.id
                    username = user.username
            except:
                pass

        report = Report(
            user_id=user_id,
            filename=file.filename,
            template_type=template,
            found_sections=found_sections,
            missing_sections=result["отсутствуют"],
            score=result["оценка"],
            status=result["статус"]
        )
        db.add(report)
        db.commit()

        result["report_id"] = report.id
        result["file"] = file.filename
        result["template"] = template
        result["user"] = username

        return result

    except Exception as e:
        return {"error": f"Check error: {str(e)}"}


@app.post("/профиль")
async def get_profile(token: str = Form(...), db: Session = Depends(get_db)):
    """Получить профиль по токену"""
    from auth import check_token
    try:
        payload = check_token(token)
        user = db.query(User).filter(User.username == payload["username"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/мои-отчеты")
async def get_my_reports(token: str = Form(...), db: Session = Depends(get_db)):
    from auth import check_token
    try:
        payload = check_token(token)
        user = db.query(User).filter(User.username == payload["username"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        reports = db.query(Report).filter(Report.user_id == user.id).order_by(Report.uploaded_at.desc()).all()
        return {
            "reports": [
                {
                    "id": report.id,
                    "file": report.filename,
                    "template": report.template_type,
                    "score": report.score,
                    "status": report.status,
                    "upload_date": report.uploaded_at.isoformat()
                }
                for report in reports
            ]
        }
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# DATABASE VIEW
@app.get("/база")
async def view_db(db: Session = Depends(get_db)):
    users = db.query(User).all()
    reports = db.query(Report).all()
    templates = db.query(ReportTemplate).all()

    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ],
        "reports": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "file": r.filename,
                "template": r.template_type,
                "score": r.score,
                "status": r.status,
                "upload_date": r.uploaded_at.isoformat() if r.uploaded_at else None
            }
            for r in reports
        ],
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "sections": json.loads(t.sections)
            }
            for t in templates
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)