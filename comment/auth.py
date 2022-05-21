from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer


class OAuthScope:
    ME = 'me'


router = APIRouter(tags=['用户登陆与注册'])

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
    scopes={
        OAuthScope.ME: '读写当前用户的信息',
    },
    auto_error=False,
)
