import enum
from collections import namedtuple
from typing import Dict, Type

from starlette import status


class ErrorCode(str, enum.Enum):
    invalid_password = 'invalid_password'
    object_not_found = 'object_not_found'


class BaseCustomError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


ApiErrorResponse = namedtuple(
    'ApiErrorResponse', ['status_code', 'error_code', 'error_message']
)
custom_errors: Dict[Type[BaseCustomError], ApiErrorResponse] = {}


def register_api_response(error: ApiErrorResponse):
    def decorator(klass):
        assert issubclass(klass, BaseCustomError)
        custom_errors[klass] = error
        return klass

    return decorator


@register_api_response(
    ApiErrorResponse(
        status.HTTP_404_NOT_FOUND,
        ErrorCode.object_not_found,
        '资源未找到',
    )
)
class ObjectNotFound(BaseCustomError):
    """资源未找到"""


@register_api_response(
    ApiErrorResponse(
        status.HTTP_400_BAD_REQUEST,
        ErrorCode.invalid_password,
        'invalid password',
    )
)
class InvalidPassword(BaseCustomError):
    """密码不合法"""
