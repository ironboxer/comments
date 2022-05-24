from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple, TypeVar

import arrow
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    Query,
    Session,
    declarative_base,
    object_session,
    relationship,
)

from comment.config import settings
from comment.exceptions import ObjectNotFound
from comment.security import create_access_token, verify_password

Base = declarative_base()


ModelType = TypeVar('ModelType', bound=Base)


class CRUDMixin:
    @classmethod
    def get(cls, db: Session, **filter_by: Any) -> Optional[ModelType]:
        return db.query(cls).filter_by(**filter_by).first()

    @classmethod
    def get_one(cls, db: Session, **filter_by: Any) -> ModelType:
        """Ensure get an object or else raise the ObjectNotFound error"""
        if not (obj := cls.get(db, **filter_by)):
            raise ObjectNotFound(
                '{} not found: {}'.format(
                    cls.__name__, ' '.join(f'{k}={v}' for k, v in filter_by.items())
                )
            )
        return obj

    @classmethod
    def get_by_id(cls, db: Session, ident: Any) -> Optional[ModelType]:
        return db.query(cls).get(ident)

    @classmethod
    def list(cls, db: Session, **kwargs: Any) -> Query:
        return db.query(cls).filter_by(**kwargs)

    @classmethod
    def create(cls, db: Session, commit: bool = True, **new: Any) -> 'ModelType':
        obj = cls(**new)
        db.add(obj)
        if commit:
            db.commit()
            db.refresh(obj)
        else:
            db.flush([obj])
        return obj

    @classmethod
    def get_or_create(cls, db: Session, **kwargs: Any) -> Tuple[ModelType, bool]:
        if not (obj := cls.get(db, **kwargs)):
            try:
                obj = cls.create(db, **kwargs)
                return obj, True
            except IntegrityError:
                db.rollback()
                obj = cls.get_one(db, **kwargs)
                return obj, False
        else:
            return obj, False

    def update(self, commit: bool = True, **new: Any) -> None:
        raise NotImplementedError

    def delete(self, commit: bool = True) -> None:
        raise NotImplementedError

    def refresh(self) -> None:
        db = object_session(self)
        db.refresh(self)


class Account(CRUDMixin, Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    username = Column(String(length=64), unique=True)
    email = Column(String(length=64), unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    auth_providers = relationship(
        'AuthProvider', back_populates='account', cascade='all, delete', lazy='dynamic'
    )
    comments = relationship(
        'Comment', back_populates='account', cascade='all, delete', lazy='dynamic'
    )

    @property
    def password_auth_provider(self) -> 'AuthProvider':
        return self.auth_providers.filter_by(
            auth_type=AuthProviderType.PASSWORD
        ).first()


class AuthProviderType:
    PASSWORD = 'pwd'


class AuthProvider(CRUDMixin, Base):
    __tablename__ = 'authprovider'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    auth_type = Column(String(length=16))
    hashed_secret = Column(String(length=255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    account = relationship('Account', back_populates='auth_providers')

    @classmethod
    def get_or_create(
        cls,
        db: Session,
        auth_type: str,
        account: Account,
    ) -> Tuple['AuthProvider', bool]:
        created = False
        provider = (
            db.query(cls)
            .filter(cls.auth_type == auth_type, cls.account_id == account.id)
            .first()
        )

        if not provider:
            created = True
            provider = cls(auth_type=auth_type, account_id=account.id)

        db.add(provider)
        db.commit()

        return provider, created

    def create_oauth_token(
        self, expire_at: Optional[datetime] = None, scopes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        expire_at = expire_at or (
            arrow.utcnow().shift(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).datetime
        )
        return {
            'access_token': create_access_token(
                self.account_id, expire_at, scopes=scopes or []
            ),
            'expire_at': expire_at,
            'user_id': self.account_id,
        }

    def verify_secret(self, raw_secret: str) -> bool:
        if self.auth_type == AuthProviderType.PASSWORD:
            return verify_password(raw_secret, self.hashed_secret)

        return False


class Comment(CRUDMixin, Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    reply_id = Column(Integer, nullable=True)
    content = Column(String(length=512))
    user_info = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    account = relationship('Account', back_populates='comments')

    @classmethod
    def list(cls, db: Session, **kwargs: Any) -> Query:
        # 0.1s slow when data is 10k
        # return db.query(cls).options(joinedload(cls.account)).order_by(desc(cls.id))
        return db.query(cls).order_by(desc(cls.id))

    @classmethod
    def bulk_create(cls, db: Session, comments: Iterable[Dict[str, Any]]) -> None:
        objects = [cls(**comment) for comment in comments]
        db.bulk_save_objects(objects)
