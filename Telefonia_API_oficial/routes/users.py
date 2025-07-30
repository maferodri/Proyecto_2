from fastapi import APIRouter, Request
from models.users import User
from models.login import Login

from controllers.users import (
    create_user,
    login
)

router = APIRouter()

@router.post("/users", response_model=User, tags=["👤 Autentication"])
async def create_user_endpoint(request: Request, user: User) -> User:
    return await create_user(user)

@router.post("/login",response_model=dict, tags=["👤 Autentication"])
async def login_access(request: Request, log: Login) -> dict:
    return await login(log)
