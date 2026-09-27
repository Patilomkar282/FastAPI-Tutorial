from fastapi import APIRouter, Depends, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from src.user.dtos import UserSchema, UserResponseSchema,LoginSchema
from src.utils.db import get_db
from src.user import contoller


user_routes=APIRouter(prefix="/users")

@user_routes.post("/register",response_model=UserResponseSchema ,status_code=status.HTTP_201_CREATED)
async def register(body:UserSchema, bg_task:BackgroundTasks, db:Session=Depends(get_db)):
    return await contoller.register(body,db,bg_task)

@user_routes.post("/login",status_code=status.HTTP_200_OK)
def login(body:LoginSchema , db:Session=Depends(get_db)):
    return contoller.login_user(body,db)

@user_routes.get("/isauth",response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
def is_auth(request:Request, db:Session=Depends(get_db)):
    return contoller.is_authenticated(request, db)
