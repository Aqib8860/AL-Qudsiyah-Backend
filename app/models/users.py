import pytz
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=True)
    last_name = Column(String, index=True, nullable=True)
    email = Column(String, index=True, nullable=True, unique=True)
    password = Column(String, nullable=True)
    number = Column(String, index=True, nullable=True)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(pytz.timezone("Asia/Kolkata")))
    last_login = Column(DateTime, nullable=True)

    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    promocodes = relationship("Promocode", back_populates="user", cascade="all, delete-orphan")
    rating_review = relationship("RatingReview", back_populates="user", cascade="all, delete-orphan")

class UserOtp(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    otp = Column(Integer, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    expires = Column(Boolean, default=False)

