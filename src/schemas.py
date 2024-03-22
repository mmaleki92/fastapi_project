# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    currency: str

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True


class SaleBase(BaseModel):
    state: str
    value: float
    fee: float
    currency: str
    client: str

class Sale(SaleBase):
    id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    id: Optional[str]

class OptionBase(BaseModel):
    text: str
    is_correct: bool

class QuestionBase(BaseModel):
    text: str
    options: List[OptionBase]

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    questions: List[QuestionBase]

class QuizCreate(QuizBase):
    pass

class Quiz(QuizBase):
    id: int

    class Config:
        orm_mode = True
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int

    class Config:
        orm_mode = True

class BlogPostBase(BaseModel):
    title: str
    content: str

class BlogPostCreate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int
    comments: List[Comment] = []

    class Config:
        orm_mode = True
