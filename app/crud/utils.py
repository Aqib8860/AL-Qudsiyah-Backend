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


def generate_name(name):
    first_name = None
    last_name = None
    if name: 
        name_list = name.split(" ")
        if name_list and len(name_list) == 2:
            first_name = name_list[0]
            last_name = name_list[1]
        else:
            first_name = name
    
    return first_name, last_name

