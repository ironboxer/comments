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
from comment.schemas import LoginInfo
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
    def list(self) -> Iterable[Comment]:
        return Comment.list(self.db)

    def create(
        self, account: Account, content: str, reply_id: Optional[int] = None
    ) -> Comment:
        if reply_id:
            try:
                Comment.get_one(self.db, id=reply_id)
            except ObjectNotFound:
                raise CommentReplyIdIncorrect

        comment = Comment.create(
            self.db, content=content, reply_id=reply_id, account_id=account.id
        )
        return comment
