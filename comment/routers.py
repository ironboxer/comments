from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from comment.db import get_db
from comment.schemas import (
    CommentResp,
    LoginPayload,
    LoginResp,
    RegisterPayload,
    UserRegisterResp,
)
from comment.services import AccountService, CommentService

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


@router.get('/comments', response_model=List[CommentResp])
def list_comments(db: Session = Depends(get_db)):
    """获取全部留言"""
    svc = CommentService(db)
    comments = svc.list()
    return CommentResp.batch_serialize(comments)
