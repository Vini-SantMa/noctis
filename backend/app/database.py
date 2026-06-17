import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

#carregar variaveis de ambient
load_dotenv()

# Puxa a url do render
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./banco.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
postgresql://postgres:Wandinha#02@db.asizpxfmfyztlsiaesth.supabase.co:5432/postgres
postgresql://postgres.asizpxfmfyztlsiaesth:Wandinha#02@aws-1-sa-east-1.pooler.supabase.com:5432/postgres
"""