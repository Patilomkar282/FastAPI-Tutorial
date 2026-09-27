from src.user.dtos import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from src.user.models import UserModel
from fastapi import HTTPException, status , Request, BackgroundTasks
from pwdlib import PasswordHash
from src.utils.settings import settings
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime,timedelta
from src.utils.mail import send_email

password_hash=PasswordHash.recommended()


def _extract_token(auth_header: str | None) -> str:
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization token")

    token = auth_header.strip()
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()
    elif " " in token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    return token


def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password,hashed_password):
    return password_hash.verify(plain_password,hashed_password)


async def register(body:UserSchema,db:Session, bg_task:BackgroundTasks):
    ##1. Username validation
    is_user=db.query(UserModel).filter(UserModel.username==body.username).first()
    if is_user:
        raise HTTPException(400,detail="Username already exist")
    ##2. Email validation 
    is_user=db.query(UserModel).filter(UserModel.email==body.email).first()
    if is_user:
        raise HTTPException(400,detail="Email already exist")

    hash_password= get_password_hash(body.password)

    new_user=UserModel(
        name=body.name,
        username=body.username,
        hash_password=hash_password,
        email=body.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    ##send email conformation 
    bg_task.add_task(send_email, [new_user.email])
   

    return {
        "id": new_user.id,
        "name": new_user.name,
        "username": new_user.username,
        "email": new_user.email,
    }


def login_user(body:LoginSchema,db:Session):
    user=db.query(UserModel).filter(UserModel.username==body.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User name not exist Wrong username")

    if not verify_password(body.password,user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password is entered")

    exp_time = datetime.now() + timedelta(minutes=settings.EXP_TIME)
    token = jwt.encode({"_id": user.id, "exp": exp_time}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {
        "token": token
    }

##token send = through headers
def is_authenticated(request:Request , db:Session):
    try: 
        token = request.headers.get("Authorization")

        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized")

        token=token.split(" ")[-1]

        data=jwt.decode(token,settings.SECRET_KEY,settings.ALGORITHM)
        print(data)
        user_id=data.get("_id")

        user=db.query(UserModel).filter(UserModel.id==user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized")

        return user
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized")



