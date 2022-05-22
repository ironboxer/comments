from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from comment.db import get_db
from comment.schemas import LoginPayload, LoginResp, RegisterPayload, UserRegisterResp
from comment.services import AccountService

router = APIRouter()


@router.post('/register', response_model=UserRegisterResp)
def register(
    payload: RegisterPayload,
    db: Session = Depends(get_db),
):
    """用户注册"""
    svc = AccountService(db)
    account = svc.register(payload.username, payload.email, payload.password)
    return UserRegisterResp.from_orm(account).dict()


@router.post('/login', response_model=LoginResp)
def login(
    payload: LoginPayload,
    db: Session = Depends(get_db),
):
    """用户登陆"""
    svc = AccountService(db)
    login_info = svc.login(payload.password, payload.username, payload.email)
    return login_info.dict()
