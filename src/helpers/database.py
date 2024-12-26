# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLite database URL
SQLITE_DATABASE_URL = "sqlite:///./src/sql_app.db"

# Create the SQLite engine with necessary arguments
engine = create_engine(SQLITE_DATABASE_URL, connect_args={'check_same_thread': False})

# Set up the session and base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
