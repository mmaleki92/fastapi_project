# routers/admin_routes.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.helpers.database import get_db
from ..models import User
from ..oauth2 import get_current_active_admin
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "../templates"))

@router.get("/admin-only-route/")
async def admin_only_route(current_admin: User = Depends(get_current_active_admin)):
    return {"message": "You are an admin!", "admin_username": current_admin.username}

@router.get("/dashboard/")
async def admin_dashboard(request: Request, db: Session = Depends(get_db), current_admin: User = Depends(get_current_active_admin)):
    if not current_admin.is_admin:
        return {"message": "You are not authorized to view this page"}

    users = db.query(User).all()
    return TEMPLATES.TemplateResponse("admin/admin_dashboard.html", {"request": request, "users": users})
