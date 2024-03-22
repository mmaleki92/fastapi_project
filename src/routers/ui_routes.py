# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from fastapi import APIRouter, Request, Depends, UploadFile, File, status, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import http3

from sqlalchemy.orm import Session
from src.helpers.database import get_db

from src import app
import src.oauth2 as oauth2
from src.config import Settings
from src import models, schemas
import numpy as np
import shutil
import os

router = APIRouter(
    tags = ['User Interface']
)

BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "../templates"))


@router.get("/", status_code=status.HTTP_200_OK)
@oauth2.auth_required
def home(request: Request, response_model=HTMLResponse):
    # Dummy data for monthly sales
    monthly_sales_data = {
        "labels": np.arange(100).tolist(), #["January", "February", "March", "April", "May", "June", "July"],
        "data": np.random.rand(100).tolist() #[10000, 15000, 8000, 20000, 18000, 25000, 30000]
    }
    
    # Pass the sales data to the template
    return TEMPLATES.TemplateResponse("home/index.html", {"request": request, "monthly_sales_data": monthly_sales_data})


@router.get("/login", status_code=status.HTTP_200_OK)
async def signin(request: Request, response_model=HTMLResponse):
    return TEMPLATES.TemplateResponse("accounts/login.html", {"request" : request})


@router.post("/login", status_code=status.HTTP_200_OK)
async def signin(request: Request):
    form = await request.form()
    form = form._dict
    form.pop('login')
    
    base_url = request.base_url
    login_url = app.auth_router.url_path_for('login')
    request_url = base_url.__str__() + login_url.__str__()[1:]

    http3client = http3.AsyncClient()
    response = await http3client.post(request_url, data=form)

    if (response.status_code==200):
        data = response.json()
        token = data['access_token']

        redirect = RedirectResponse(url=router.url_path_for('home'))
        redirect.status_code = 302
        #TODO: secure and httponly
        # redirect.set_cookie('Authorization', f'Bearer {token}', httponly=True, secure=True)

        redirect.set_cookie('Authorization', f'Bearer {token}', httponly=True, secure=True)
        return redirect

    if (response.status_code==500):
        msg = 'Issue with the Server'

    get_users_url = app.user_router.url_path_for('get_users')
    users_request_url = base_url.__str__() + get_users_url.__str__()[1:]
    http3client2 = http3.AsyncClient()
    test_response = await http3client2.get(users_request_url)
    test_users = test_response.json()
    msg = 'Wrong User or Password'
    for test_user in test_users:
        print (test_user)
        if form['username']==test_user['email']:
            msg = 'Password is Wrong'
        
    return TEMPLATES.TemplateResponse("accounts/login.html", {"request" : request, "msg" : msg})


@router.get("/register", status_code=status.HTTP_200_OK)
async def register(request: Request, response_model=HTMLResponse):
    return TEMPLATES.TemplateResponse("accounts/register.html", {"request" : request})


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(request: Request, response_model=HTMLResponse):
    form = await request.form()
    form_dict = dict(form)  # Convert to regular dict
    form_dict.pop('register', None)  # Safely remove 'register' key if it exists
    form = form_dict
    print(form_dict)
    #validates the form data
    new_user = models.User(**form)

    base_url = request.base_url
    create_user_url = app.user_router.url_path_for('create_user')
    request_url = base_url.__str__() + create_user_url.__str__()[1:]
    http3client = http3.AsyncClient()
    response = await http3client.post(request_url, json=form)

    if (response.status_code==201):
        redirect = RedirectResponse(url=router.url_path_for('signin'))
        # default redirect is 307, which maintains the reused 'POST' indictation, 302 changes it to 'GET'
        redirect.status_code = 302
        return redirect

    msg = 'Something Went Wrong'
    if (response.status_code==500):
        msg = 'Issue with the Server'

    get_users_url = app.user_router.url_path_for('get_users')
    users_request_url = base_url.__str__() + get_users_url.__str__()[1:]
    http3client2 = http3.AsyncClient()
    test_response = await http3client2.get(users_request_url)
    test_users = test_response.json()
    for test_user in test_users:
        if new_user.email==test_user['email']:
            msg = 'Email Already Registered'
        if new_user.username == test_user['username']:
            msg = 'Username Already Registered '

    return TEMPLATES.TemplateResponse("accounts/register.html", {"request" : request, "msg" : msg })

@router.get('/tables', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def tables(request: Request):
    return TEMPLATES.TemplateResponse("home/tables.html", {"request" : request})


@router.get('/billing', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def billing(request: Request):
    return TEMPLATES.TemplateResponse("home/billing.html", {"request" : request})

@router.get('/virtual-reality', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def virtual_reality(request: Request):
    return TEMPLATES.TemplateResponse("home/virtual-reality.html", {"request" : request})


@router.post("/users/{user_id}/upload-image")
async def upload_user_image(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    file_extension = Path(file.filename).suffix
    if file_extension not in ['.jpg', '.jpeg', '.png']:
        raise HTTPException(status_code=400, detail="Invalid file format")

    # Ensure the target directory exists
    target_dir = Path("src/static/profile_imgs")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Determine the file's destination path
    file_path = target_dir / f"{user_id}_{file.filename}"
    
    # Open a file at the destination path for writing and copy the uploaded file's contents
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Optionally, store a relative path or just the filename in your database
    user.image_url = file_path.name  # Storing just the filename for simplicity
    db.commit()

    return {"filename": file.filename}


@router.get('/profile', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def profile(request: Request,  user_id: int = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    print("*"*40)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    # Now `user` contains all the information about the user, including `image_url`
    return  TEMPLATES.TemplateResponse("home/profile.html", {"request": request, "user": user})


@router.get('/rtl', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def rtl(request: Request):
    return TEMPLATES.TemplateResponse("home/rtl.html", {"request" : request})

@router.get('/settings', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def settings(request: Request):
    return TEMPLATES.TemplateResponse("home/settings.html", {"request": request})

@router.get('/music_player', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def music_player(request: Request):
    return TEMPLATES.TemplateResponse("home/music_player.html", {"request": request})


@router.get('/game', status_code=status.HTTP_200_OK)
@oauth2.auth_required
def game(request: Request):
    return TEMPLATES.TemplateResponse("home/game.html", {"request": request})


@router.get("/quiz", name="quiz")
@oauth2.auth_required
def quiz(request: Request):
    quiz_dict = {
        "questions": [
            {
                "id": 1,
                "text": "What is the capital of France?",
                "options": [
                    {"id": 1, "text": "Paris"},
                    {"id": 2, "text": "London"},
                    {"id": 3, "text": "Berlin"},
                ],
            },
            # Add more questions as needed
        ]
    }
    return TEMPLATES.TemplateResponse("home/quiz.html", {"request": request, "quiz": quiz_dict})

@router.post('/submit-quiz', status_code=status.HTTP_200_OK)
async def submit_quiz(request: Request):
    form_data = await request.form()
    # Process the submitted answers
    # This is where you'd check the answers and calculate the score
    results = {}
    return TEMPLATES.TemplateResponse("home/quiz_results.html", {"request": request, "results": results})

