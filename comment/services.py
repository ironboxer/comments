from typing import Iterable, Optional

from sqlalchemy.orm import Session

from comment.auth import OAuthScope
from comment.exceptions import (
    CommentReplyIdIncorrect,
    EmailAlreadyUsed,
    ObjectNotFound,
    PasswordIncorrect,
    UsernameAlreadyUsed,
    UsernameEmailCannotBothBeNone,
)
from comment.models import Account, AuthProvider, AuthProviderType, Comment
from comment.schemas import CommentResp, LoginInfo, UserInfo
from comment.security import get_password_hash


class BaseService:
    def __init__(self, db: Session):
        self.db = db


class AccountService(BaseService):
    def register(self, username: str, email: str, password: str) -> Account:
        if Account.get(self.db, username=username):
            raise UsernameAlreadyUsed
        if Account.get(self.db, email=email):
            raise EmailAlreadyUsed

        account = Account.create(self.db, username=username, email=email)
        AuthProvider.create(
            self.db,
            auth_type=AuthProviderType.PASSWORD,
            account_id=account.id,
            hashed_secret=get_password_hash(password),
        )
        return account

    def login(
        self, password: str, username: Optional[str] = None, email: Optional[str] = None
    ) -> LoginInfo:
        if not (username or email):
            raise UsernameEmailCannotBothBeNone

        if username:
            account = Account.get_one(self.db, username=username)
        else:
            account = Account.get_one(self.db, email=email)

        provider: AuthProvider = account.password_auth_provider
        if not provider.verify_secret(password):
            raise PasswordIncorrect

        token = provider.create_oauth_token(scopes=[OAuthScope.ME])
        return LoginInfo(**token)


class CommentService(BaseService):
    def list(self) -> Iterable[CommentResp]:
        result = []
        comments = Comment.list(self.db).all()
        comments_dict = {c.id: CommentResp.serialize(c) for c in comments}
        for comment in comments:
            comment_dic = comments_dict[comment.id]
            if comment.reply_id:
                comments_dict[comment.reply_id]['sub_comments'].append(comment_dic)
            else:
                result.append(comment_dic)

        return result

    def create(
        self, account: Account, content: str, reply_id: Optional[int] = None
    ) -> Comment:
        if reply_id:
            try:
                Comment.get_one(self.db, id=reply_id)
            except ObjectNotFound:
                raise CommentReplyIdIncorrect

        user_info = UserInfo.serialize(account)
        comment = Comment.create(
            self.db,
            content=content,
            reply_id=reply_id,
            account_id=account.id,
            user_info=user_info,
        )
        return comment
