import re

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field, validator

from comment.exceptions import InvalidPassword


class RegisterPayload(BaseModel):
    username: str = Field(
        min_length=5, max_length=20, regex=r'[a-zA-Z0-9]+', description='用户名'
    )
    password: str = Field(min_length=8, max_length=20, description='密码')
    email: EmailStr = Field(description='邮箱')

    @validator('password')
    def validate_password(cls, v):
        if not (
            re.search(r'[A-Z]+', v)
            or re.search(r'[a-z]+', v)
            or re.search(r'[0-9]+', v)
            or re.search(r'[^A-Za-z0-9]+', v)
        ):
            raise InvalidPassword

        return v


router = APIRouter(tags=['router'])
