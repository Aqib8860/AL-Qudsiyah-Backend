from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal

from crud.auth import hash_password, get_current_user
from crud.users import (
    user_register_view, user_login_view, update_user_by_admin_view, user_list_view, user_otp_verify_view, resend_otp_view, check_email_view,
    get_user_view, delete_user_by_admin_view
)

from schemas.users import RegisterBase, LoginBase, AdminUpdateUserBase, UserBase, OtpVerify

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User Registration
@router.post("/user/registration/")
async def user_register(user: RegisterBase, db: Session = Depends(get_db)):
    unsafe_password = user.password
    user.password = hash_password(user.password)
    return await user_register_view(db=db, user=user, unsafe_password=unsafe_password)


# User Login
@router.post("/user/login/")
async def user_register(login_user: LoginBase, db: Session = Depends(get_db)):
    return await user_login_view(db=db, login_user=login_user)


# OTP Verify
@router.post("/user/verify/")
async def user_otp_verify(data: OtpVerify, db: Session = Depends(get_db)):
    return await user_otp_verify_view(db=db, data=data)


# Resend OTP
@router.get("/user/resend-otp/")
async def resend_otp(email: str, db: Session = Depends(get_db)):

    return await resend_otp_view(db=db, email=email)


# Check Email already exists
@router.get("/user/check-email/{email}/")
async def check_email(email: str, db: Session = Depends(get_db)):
    return await check_email_view(db=db, email=email)


# Update User - By Admin
@router.patch("/admin/user/{user_id}/", response_model=UserBase)
async def update_user_by_admin(
    user_id: int,
    updated_user: AdminUpdateUserBase, 
    db: Session = Depends(get_db)
):
    return await update_user_by_admin_view(db=db, user_id=user_id, updated_user=updated_user)


# Update User - By Admin
@router.delete("/admin/user/{user_id}/", response_model=UserBase)
async def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db)
):
    return await delete_user_by_admin_view(db=db, user_id=user_id)



@router.get("/admin/users-list/", response_model=list[UserBase])
async def users_list(db: Session = Depends(get_db)):
    return await user_list_view(db=db)


@router.get("/user/", response_model=UserBase)
async def user(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await get_user_view(db=db, user=user)
