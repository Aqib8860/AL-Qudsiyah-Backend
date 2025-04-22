from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

from models.users import User, UserOtp
from crud.auth import verify_password, create_access_token, verify_google_token
from crud.send_mail import send_email
from crud.utils import generate_otp, generate_name
from schemas.users import RegisterBase, LoginBase, AdminUpdateUserBase, UserBase, OtpVerify


# User Registeration
async def user_register_view(db: Session, user: RegisterBase, unsafe_password: str):
    try:
        if unsafe_password != user.confirm_password:
            return JSONResponse({"error": "Password not matched"}, status_code=400)

        is_exists = db.query(User).filter(User.email == user.email).first()
        if is_exists:
            return JSONResponse({"error": "Email already exists"}, status_code=400)

        db_user = User(email=user.email, password=user.password, first_name=user.first_name, last_name=user.last_name)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        otp = await generate_otp(db, user.email)
        await send_email(user.email, otp)
        return JSONResponse({"msg": "Registration success"}, status_code=200)

    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=400)        


# USer OTP Verify
async def user_otp_verify_view(db: Session, data:OtpVerify):
    try:
        # Step 1: Get the most recent unexpired OTP for the email
        otp_record = (
            db.query(UserOtp)
            .filter(UserOtp.email == data.email, UserOtp.expires == False)
            .order_by(UserOtp.created_at.desc())
            .first()
        )

        if not otp_record:
            return JSONResponse({"error": "No active OTP found for this email."}, status_code=400)

        # Step 2: Check if OTP matches
        if otp_record.otp != data.otp:
            return JSONResponse({"error": "Invalid OTP."}, status_code=400)

        # Step 3: Check if OTP is within 10 minutes
        time_diff = datetime.now() - otp_record.created_at
        if time_diff > timedelta(minutes=10):
            otp_record.expires = True
            db.commit()
            return JSONResponse({"error": "OTP expired."}, status_code=400)

        # Step 4: Mark OTP as used/expired
        otp_record.expires = True
        db.commit()

        # Step 5 Active the user
        db.query(User).filter(User.email == data.email).update({User.is_active: True})
        db.commit()

        return JSONResponse({"msg": "OTP verified successfully."}, status_code=200)

    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)
    

# Resend OTP
async def resend_otp_view(db:Session, email: str):
    try:
        user_exists = db.query(User).filter(User.email == email, User.is_active == False).first()

        if not user_exists:
            return JSONResponse({"error": "Access Denied User does not exists or already active"}, status_code=500)

        otp = await generate_otp(db, email)
        await send_email(email, otp)
        return JSONResponse({"msg": "otp sent"})
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)


# Check email already exists
async def check_email_view(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return JSONResponse({"msg": "Email exists", "exists": True})
    
    return JSONResponse({"msg": "Email not exists", "exists": False})


# User Login
async def user_login_view(db: Session, login_user: LoginBase):
    try:
        # Case 1 Google Login
        if login_user.access_token:
            google_user = verify_google_token(login_user.access_token)

            email = google_user["email"]
            name = google_user.get("name", "")
            first_name, last_name = generate_name(name)

            phone = google_user.get("phone", "")

            # Check if user exists in DB
            user = db.query(User).filter(User.email == email).first()

            if not user:
                # Create a new account if Google login is used for the first time
                
                db_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=None,  # No password for Google login
                    number=phone,
                    is_active=True,
                    created_at=datetime.now(),
                    last_login=datetime.now()
                )
                # Save User
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                
                # Get User
                user = db.query(User).filter(User.id == db_user.id).first()

            # Generate JWT token
            access_token = create_access_token(data={"sub": user.email, "id": str(user.id)})

        # Case 2: Manual Login (Email & Password)
        else:
            user = db.query(User).filter(User.email == login_user.email).first()
            if not user:
                return JSONResponse({"error": "Incorrect Email"}, status_code=400)
            
            if not verify_password(login_user.password, user.password):
                return JSONResponse({"error": "Incorrect Password"}, status_code=400)

            if not user.is_active:
                return JSONResponse({"error": "User is not active"}, status_code=400)

            # ✅ Update last_login
            user.last_login = datetime.now()
            db.commit()

            # Generate JWT token
            access_token = create_access_token(data={"sub": user.email, "id": str(user.id)})

        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": {
                "id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name, 
                "is_active": user.is_active, "is_admin": user.is_admin
                },
            }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# Update User By Admin
async def update_user_by_admin_view(db: Session, user_id: int, updated_user:AdminUpdateUserBase):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse({"error": "User not exists"}, status_code=400)
        
        # Update only the fields provided in the request
        for field, value in updated_user.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)

        return user
    
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=400)

# Delete User By Admin
async def delete_user_by_admin_view(db: Session, user_id: int):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse({"error": "User not found"}, status_code=404)
        
        db.delete(user)
        db.commit()

        return JSONResponse({"message": "User deleted successfully"}, status_code=200)
    
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=400)


async def user_list_view(db: Session):
    users = db.query(User)
    return users


async def get_user_view(db: Session, user: dict):
    try:
    
        user_data = db.query(User).filter(User.id == user["id"]).first()
        if not user:
            return JSONResponse({"error": "User not exists"}, status_code=400)
        return user_data
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


