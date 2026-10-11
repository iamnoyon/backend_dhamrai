from app.core.db import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from .schema import UserRegisterSchema, LoginSchema
from app.core.security import get_current_user
from app.modules.users.model import User

from .service import user_register_service, login_service, get_me_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(req: UserRegisterSchema, db: Session = Depends(get_db)):
    return await user_register_service(req, db)


@router.post("/login", summary="Superadmin login, returns a jwt access token")
async def login(req: LoginSchema, db: Session = Depends(get_db)):
    return await login_service(req, db)


@router.get("/me", summary="Get the logged in user")
async def me(user: User = Depends(get_current_user)):
    return await get_me_service(user)
