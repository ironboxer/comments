from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from comment.auth import get_current_user
from comment.db import get_db
from comment.models import Account
from comment.schemas import (
    CommentPayload,
    CommentResp,
    LoginInfo,
    LoginPayload,
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
    return UserRegisterResp.serialize(account)


@router.post('/login', response_model=LoginInfo)
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


@router.post(
    '/comments', response_model=CommentResp, status_code=status.HTTP_201_CREATED
)
def post_comment(
    payload: CommentPayload,
    db: Session = Depends(get_db),
    login: Account = Depends(get_current_user),
):
    """创建留言"""
    svc = CommentService(db)
    comment = svc.create(login, payload.content, payload.reply_id)
    return CommentResp.serialize(comment)
