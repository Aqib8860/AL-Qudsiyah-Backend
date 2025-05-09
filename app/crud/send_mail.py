# config.py
import random
from datetime import datetime
from pydantic import BaseModel, EmailStr
from fastapi_mail import ConnectionConfig
import os
from dotenv import load_dotenv
# main.py
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType
from pathlib import Path


load_dotenv()


async def send_email(email, otp):
    conf = ConnectionConfig(
        MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
        MAIL_FROM = os.getenv("MAIL_FROM"),
        MAIL_PORT = int(os.getenv("MAIL_PORT")),
        MAIL_SERVER = os.getenv("MAIL_SERVER"),
        MAIL_STARTTLS = True,
        MAIL_SSL_TLS = False,
        USE_CREDENTIALS = True,
        VALIDATE_CERTS = True
    )

    # 1. Get current year
    year = str(datetime.now().year)

    # 2. Read and fill the template
    template_path = Path("templates/registration-mail.html")
    html = template_path.read_text()
    html = html.replace("{{ otp }}", otp).replace("{{ year }}", year)


    # 3. Send email
    message = MessageSchema(
        subject="Your OTP for AL Qudsiyah",
        recipients=[email],  # must be a list
        body=html,
        subtype=MessageType.html  # or plain if not using HTML
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    # await background_tasks = BackgroundTasks
    # background_tasks.add_task(fm.send_message, message)

    return

from jinja2 import Environment, FileSystemLoader

async def send_order_confirm_mail(payment, order, products_name):
    print("Send mail function")
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_PORT=int(os.getenv("MAIL_PORT")),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

    # Get current year
    year = str(datetime.now().year)

    # Get Customer name
    customer_name = f"{payment.user.first_name}"

    amount = payment.amount_paid
    payment_method = payment.payment_method
    payment_date = payment.paid_on
    email = payment.user.email

    # Products purchased (as a list of strings)
    products = products_name

    # Prepare the data for the template
    context = {
        "customer_name": customer_name,
        "amount": amount,
        "payment_method": payment_method,
        "date": payment_date.strftime("%d %B %Y"),  # Format date
        "year": year,
        "products": products
    }
    print("Line 93")
    # Set up Jinja2 environment to load templates
    template_loader = FileSystemLoader("templates")
    env = Environment(loader=template_loader)
    template = env.get_template("order-success-mail.html")

    # Render the template with the data
    html = template.render(context)

    # 3. Send email
    message = MessageSchema(
        subject="Your Payment Confirmation from AL Qudsiyah",
        recipients=[email],  # must be a list
        body=html,
        subtype=MessageType.html  # or plain if not using HTML
    )
    print("Line 109")
    fm = FastMail(conf)
    await fm.send_message(message)
    print("Line 112")

    return