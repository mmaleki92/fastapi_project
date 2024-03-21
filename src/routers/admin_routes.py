# routers/admin_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.helpers.database import get_db
from ..models import User
from ..oauth2 import get_current_active_admin

router = APIRouter()

@router.get("/admin-only-route/")
async def admin_only_route(current_admin: User = Depends(get_current_active_admin)):
    return {"message": "You are an admin!", "admin_username": current_admin.username}
