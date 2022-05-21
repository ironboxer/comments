from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuthProviderType:
    PASSWORD = 'pwd'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AuthProvider(Base):
    __tablename__ = 'auths'

    id = Column(Integer, primary_key=True)
    auth_type = Column(String(length=16))
    hashed_secret = Column(String(length=255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
