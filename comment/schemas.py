import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, root_validator, validator

from comment.exceptions import PasswordInvalidFormat
from comment.models import Account, Comment
from comment.utils.time import time_2_iso_format


class RegisterPayload(BaseModel):
    username: str = Field(
        min_length=5,
        max_length=20,
        regex=r'[a-zA-Z0-9]+',
        description='用户名：不可为空，只能使用字母和数字，长度在 5 ~ 20 之间',
    )
    email: EmailStr = Field(description='邮箱：不可为空，格式要正确')
    password: str = Field(
        min_length=8,
        max_length=20,
        description='密码：不可为空，长度在 8 ~ 20 之间，至少包含一个大写、一个小写、一个数字、一个特殊符号',
    )

    @validator('password')
    def validate_password(cls, v):
        if not (
            re.search(r'[A-Z]+', v)
            and re.search(r'[a-z]+', v)
            and re.search(r'[0-9]+', v)
            and re.search(r'[^A-Za-z0-9]+', v)
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
    content: str = Field(min_length=3, max_length=200, description='留言：长度在 3 ~ 200 字之间')


class LoginInfo(BaseModel):
    user_id: int = Field(description='用户 ID')
    access_token: str = Field(description='Access Token')
    token_type: str = Field(default='Bearer', description='Token 类型')
    expire_at: datetime = Field(description='创建时间')


class UserInfo(BaseModel):
    id: int = Field(description='用户 ID')
    username: str = Field(description='用户名')

    class Config:
        orm_mode = True

    @classmethod
    def serialize(cls, user: Account) -> Dict[str, Any]:
        return {
            'id': user.id,
            'username': user.username,
        }


class UserResp(UserInfo):
    email: str = Field(description='邮箱')
    created_at: datetime = Field(description='创建时间')

    @classmethod
    def serialize(cls, user: Account) -> Dict[str, Any]:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': time_2_iso_format(user.created_at),
        }


class CommentResp(BaseModel):
    id: int = Field(description='留言 ID')
    reply_id: Optional[int] = Field(default=None, description='被回复的留言 ID')
    content: str = Field(description='留言内容')
    created_at: datetime = Field(description='留言创建时间')
    user_info: UserInfo = Field(description='留言的用户基本信息')
    sub_comments: List['CommentResp'] = Field(default=[], description='子留言')

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
