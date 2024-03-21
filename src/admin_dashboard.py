from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from src.helpers.database import get_db
from src.oauth2 import get_current_user, get_current_active_admin

app = FastAPI()

# Assuming get_current_user and get_current_active_admin are functions you have defined to authenticate and authorize users

@app.get("/admin/users/", response_model=List[schemas.UserOut], dependencies=[Depends(get_current_active_admin)])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users
