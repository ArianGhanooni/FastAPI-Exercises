from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Core.Database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # User expense history relationship
    payment_history = relationship(
        "Payment_History",
        back_populates="user",
        cascade="all, delete-orphan")

    # User refresh token sessions
    sessions = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan")