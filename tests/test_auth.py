import pytest
from fastapi import HTTPException

from comment.auth import OAuthScope, get_current_user
from comment.config import settings
from comment.security import create_access_token, encode_jwt
from comment.utils.time import shifted_datetime


def test_get_current_user(db, user1, access_token1):
    account = get_current_user(db, access_token1)
    assert account == user1


@pytest.mark.parametrize('access_token', [None, '', 'hella.asdsb.dddc'])
def test_get_current_user_with_invalid_token(db, access_token):
    with pytest.raises(HTTPException):
        get_current_user(db, access_token)


@pytest.mark.usefixtures('user1')
def test_get_current_user_with_incorrect_token(db):
    user_id = 1111
    expire_at = shifted_datetime(None, minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user_id, expire_at, scopes=[OAuthScope.ME])
    with pytest.raises(HTTPException):
        get_current_user(db, token)


def test_get_current_user_with_invalid_format(db, user1):
    expire_at = shifted_datetime(None, minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = encode_jwt(
        {'exp': expire_at, 'subbbbb': str(user1.id), 'scopes': [OAuthScope.ME]}
    )
    with pytest.raises(HTTPException):
        get_current_user(db, token)
