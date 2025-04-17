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

