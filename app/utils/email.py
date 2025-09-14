from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi import BackgroundTasks
from pydantic import EmailStr
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.config import mail_config, SECRET_KEY, ALGORITHM

def create_email_verification_token(email: EmailStr):
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode = {"exp": expire, "sub": email, "scope": "email_verification"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def send_verification_email(email: EmailStr, username: str, token: str, background_tasks: BackgroundTasks):
    verification_url = f"http://localhost:8000/api/v1/auth/verify-email?token={token}"
    
    # Шаблон листа для верифікації
    html_content = f"""
    <html>
    <head>
        <title>Підтвердження електронної пошти</title>
    </head>
    <body>
        <h3>Вітаємо, {username}!</h3>
        <p>Дякуємо за реєстрацію в нашому сервісі контактів.</p>
        <p>Для підтвердження вашої електронної пошти, будь ласка, перейдіть за наступним посиланням:</p>
        <p><a href="{verification_url}">{verification_url}</a></p>
        <p>Посилання дійсне протягом 24 годин.</p>
        <p>Якщо ви не реєструвалися в нашому сервісі, проігноруйте цей лист.</p>
        <p>З повагою,<br>Команда Contacts API</p>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Підтвердження електронної пошти",
        recipients=[email],
        body=html_content,
        subtype=MessageType.html
    )
    
    fm = FastMail(mail_config)
    background_tasks.add_task(fm.send_message, message)