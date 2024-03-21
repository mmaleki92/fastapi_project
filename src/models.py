# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from src.helpers.database import Base

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)  # New admin flag


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, nullable=False)
    state = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    client = Column(String, nullable=False)
    
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    product = relationship("Product")

class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    text = Column(String, nullable=False)
    quiz = relationship("Quiz", back_populates="questions")

class Option(Base):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'))
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
    question = relationship("Question", back_populates="options")

Quiz.questions = relationship("Question", order_by=Question.id, back_populates="quiz")
Question.options = relationship("Option", order_by=Option.id, back_populates="question")
