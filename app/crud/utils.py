import random
from datetime import datetime
from models.users import UserOtp


async def generate_otp(db, email):
    # Step 0: Expire all previous OTPs for this email
    db.query(UserOtp).filter(UserOtp.email == email, UserOtp.expires == False).update({UserOtp.expires: True})
    db.commit()

    # Step 1: Generate OTP
    otp = str(random.randint(100000, 999999))

    # Step 2: Save OTP to the database
    otp_entry = UserOtp(otp=otp, email=email, created_at=datetime.now(), expires=False)
    db.add(otp_entry)
    db.commit()

    return otp

