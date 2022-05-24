from datetime import datetime
from typing import Any, Dict, Union

from jose import jwt
from passlib.context import CryptContext

from comment.config import settings

PWD_CONTEXT = CryptContext(schemes=['argon2'], deprecated='auto')


ALGORITHM = 'HS256'


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def encode_jwt(payload: Dict[str, Any]) -> str:
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)


def create_access_token(
    subject: Union[str, Any],
    expire: datetime,
    **custom: Dict[str, Any],
):
    return encode_jwt({'exp': expire, 'sub': str(subject), **custom})
