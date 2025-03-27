from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///loan_management.sqlite3" , echo = False,connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autoflush=False,bind = engine, expire_on_commit=False)

Base = declarative_base()
