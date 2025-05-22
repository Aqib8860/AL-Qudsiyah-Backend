import random
from datetime import datetime
from models.users import UserOtp
from models.products import Payment


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


async def get_order_payment_details(db, order):
    try:
        # Get User All Payments
        user_paments = db.query(Payment).filter(Payment.user_id == order.user_id)

        payment_detail = None
        
        for payment in user_paments:
            if payment.orders:
                payment_orders = payment.orders.split(",")

                if str(order.id) in payment_orders:
                    payment_detail = payment
        
        if payment_detail:
            return {
                "id": payment_detail.id,
                "order_ids": payment_detail.orders,
                "address": payment_detail.address,
                "customer_phone": payment_detail.customer_phone,
                "amount_paid": payment_detail.amount_paid,
                "payment_method": payment_detail.payment_method,
                "promocode": payment_detail.promocode,
                "paid_on": payment_detail.paid_on,
                "transaction_no": payment_detail.transaction_no,
                "status": payment_detail.status,
                "created_on": payment_detail.created_on,
            }

        return payment_detail
    except Exception as e:
        return None

