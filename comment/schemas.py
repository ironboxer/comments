import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, root_validator, validator

from comment.exceptions import PasswordInvalidFormat
from comment.models import Account, Comment
from comment.utils.time import time_2_iso_format


class RegisterPayload(BaseModel):
    username: str = Field(
        min_length=5, max_length=20, regex=r'[a-zA-Z0-9]+', description='用户名'
    )
    email: EmailStr = Field(description='邮箱')
    password: str = Field(min_length=8, max_length=20, description='密码')

    @validator('password')
    def validate_password(cls, v):
        if not (
            re.search(r'[A-Z]+', v)
            or re.search(r'[a-z]+', v)
            or re.search(r'[0-9]+', v)
            or re.search(r'[^A-Za-z0-9]+', v)
        ):
            raise PasswordInvalidFormat

        return v


class LoginPayload(BaseModel):
    username: Optional[str] = Field(
        min_length=5,
        max_length=20,
        regex=r'[a-zA-Z0-9]+',
        description='用户名',
        default=None,
    )
    email: Optional[EmailStr] = Field(description='邮箱', default=None)
    password: str = Field(min_length=8, max_length=20, description='密码')

    @root_validator
    def validate_data(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not (values.get('username') or values.get('email')):
            pass

        return values


class CommentPayload(BaseModel):
    reply_id: Optional[int] = Field(description='父留言ID', default=None)
    content: str = Field(min_length=3, max_length=200, description='留言')


class LoginInfo(BaseModel):
    user_id: int
    access_token: str
    token_type: str = 'Bearer'
    expire_at: datetime


class UserInfo(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

    @classmethod
    def serialize(cls, user: Account) -> Dict[str, Any]:
        return {
            'id': user.id,
            'username': user.username,
        }


class UserResp(UserInfo):
    email: str
    created_at: datetime

    @classmethod
    def serialize(cls, user: Account) -> Dict[str, Any]:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': time_2_iso_format(user.created_at),
        }


class CommentResp(BaseModel):
    id: int
    reply_id: Optional[int] = None
    content: str
    created_at: datetime
    user_info: UserInfo
    sub_comments: List['CommentResp'] = []

    @classmethod
    def serialize(cls, comment: Comment) -> Dict[str, Any]:
        return {
            'id': comment.id,
            'reply_id': comment.reply_id,
            'content': comment.content,
            'created_at': time_2_iso_format(comment.created_at),
            'user_info': comment.user_info,
            # 'user_info': UserInfo.serialize(comment.account),
            'sub_comments': [],
        }
