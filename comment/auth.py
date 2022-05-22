from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError
from sqlalchemy.orm import Session
from starlette import status

from comment.db import get_db
from comment.models import Account
from comment.security import decode_jwt


class OAuthScope:
    ME = 'me'


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/login',
    scopes={
        OAuthScope.ME: '读写当前用户的信息',
    },
    auto_error=False,
)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


def get_current_user(
    security_scopes: SecurityScopes,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Account:
    """获取当前登录的用户信息"""
    if not token:
        raise credentials_exception

    try:
        payload = decode_jwt(token)
    except JWTError:
        raise credentials_exception

    if not (user_id := payload.get('sub')):
        raise credentials_exception

    if not (user := Account.get(db, id=user_id)):
        raise credentials_exception

    return user
