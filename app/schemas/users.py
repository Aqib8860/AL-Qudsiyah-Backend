from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class RegisterBase(BaseModel):
    first_name: str
    last_name: str | None = None
    email: str
    password: str
    confirm_password: str


class OtpVerify(BaseModel):
    email: str
    otp: int


class LoginBase(BaseModel):
    email: str
    password: str | None =  None  # Optional for Google login
    access_token: str | None = None # Optional for Oauth2 token


class UserBase(BaseModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    number: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    created_at: datetime | None = None
    last_login: datetime | None = None


class AdminUpdateUserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    number: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    