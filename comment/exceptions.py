import enum
from collections import namedtuple
from typing import Dict, List, Optional, Type

from pydantic import BaseModel, Field
from starlette import status


class ErrorCode(str, enum.Enum):
    request_validation_error = 'request_validation_error'
    object_not_found = 'object_not_found'
    password_invalid_format = 'password_invalid_format'
    password_incorrect = 'password_incorrect'
    username_email_cannot_both_be_none = 'username_email_cannot_both_be_none'
    username_already_used = 'username_already_used'
    email_already_used = 'email_already_used'
    comment_reply_id_incorrect = 'comment_reply_id_incorrect'


class ErrorResponseDetailMessage(BaseModel):
    loc: List[str] = Field(..., description='错误字段的位置')
    msg: str = Field(..., description='错误消息')
    type: str = Field(..., description='错误类型')


class ErrorResponseScheme(BaseModel):
    code: str = Field(..., description='错误代码')
    message: str = Field(..., description='错误消息')
    detail: Optional[List[ErrorResponseDetailMessage]] = Field(
        None, description='可选, 详细的错误信息'
    )


class BaseCustomError(Exception):
    def __init__(self, message: str = None) -> None:
        self.message = message


ApiErrorResponse = namedtuple('ApiErrorResponse', ['status_code', 'code', 'message'])
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
        ErrorCode.password_invalid_format,
        'password invalid format',
    )
)
class PasswordInvalidFormat(BaseCustomError):
    """密码格式错误"""


@register_api_response(
    ApiErrorResponse(
        status.HTTP_400_BAD_REQUEST, ErrorCode.password_incorrect, 'password incorrect'
    )
)
class PasswordIncorrect(BaseCustomError):
    """密码错误"""


@register_api_response(
    ApiErrorResponse(
        status.HTTP_400_BAD_REQUEST,
        ErrorCode.username_email_cannot_both_be_none,
        'username or password cannot both be none',
    )
)
class UsernameEmailCannotBothBeNone(BaseCustomError):
    """用户名和邮箱不能同时为空"""


@register_api_response(
    ApiErrorResponse(
        status.HTTP_400_BAD_REQUEST,
        ErrorCode.username_already_used,
        'username already used',
    )
)
class UsernameAlreadyUsed(BaseCustomError):
    """用户名已占用"""


@register_api_response(
    ApiErrorResponse(
        status.HTTP_400_BAD_REQUEST,
        ErrorCode.email_already_used,
        'email already used',
    )
)
class EmailAlreadyUsed(BaseCustomError):
    """邮箱已占用"""


@register_api_response(
    ApiErrorResponse(
        status.HTTP_400_BAD_REQUEST,
        ErrorCode.comment_reply_id_incorrect,
        'comment reply_id incorrect',
    )
)
class CommentReplyIdIncorrect(BaseCustomError):
    """留言的reply_id错误"""
