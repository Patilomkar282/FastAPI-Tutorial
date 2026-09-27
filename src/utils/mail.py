from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List



conf = ConnectionConfig(
    MAIL_USERNAME = "Patilomkar2820@gmail.com",
    MAIL_PASSWORD = "vcdb voby lbnj jaqx",
    MAIL_FROM = "Patilomkar2820@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Omkar Patil",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# app = FastAPI()



async def send_email(emails: List[str]):
    html = """<p>Hi Thanks for contacting Omkar Patil will get you back</p> """

    message = MessageSchema(
        subject="Omkar Patil",
        recipients=emails,
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    print({"message": "Mail is sent successfully"})
