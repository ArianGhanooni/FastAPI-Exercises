from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import relationship

# ---------------------- Database Config ---------------------- #
# SQLite database file location
SQLALCHEMY_DATABASE_URI = "sqlite:////payment.db"
# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URI,
                       connect_args={"check_same_thread": False},)
# Create session factory
session = sessionmaker(autocommit = False, autoflush = False, bind=engine)
# Base class for all SQLAlchemy models
Base = declarative_base()

# ---------------------- Database Dependency ---------------------- #
# Create and close database session for each request
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()