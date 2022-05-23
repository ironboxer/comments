import logging

from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic import command
from alembic.config import Config
from comment.config import settings
from comment.db import Session as DBSession
from comment.db import engine as db_engine
from comment.models import Account, Comment
from comment.schemas import UserInfo
from comment.services import AccountService

LOGGER = logging.getLogger(__file__)


def prepare_user(db: Session, username: str, email: str, password: str) -> Account:
    LOGGER.info('prepare user: %s, %s, %s', username, email, password)
    svc = AccountService(db)
    account = svc.register(username, email, password)
    return account


def prepare_comments(db: Session, user: Account):
    LOGGER.info('prepare comments')
    comments = [
        {
            'id': i,
            'reply_id': (i - 1) // 10 * 10,
            'content': f'content {i}',
            'account_id': user.id,
            'user_info': UserInfo.serialize(user),
        }
        for i in range(1, settings.DEFAULT_COMMENTS_COUNT + 1)
    ]
    for comment in comments:
        if comment['reply_id'] == 0:
            comment['reply_id'] = None

    Comment.bulk_create(db, comments)
    db.commit()


def prepare_data():
    LOGGER.info('prepare data...')
    username, email, password = 'User1', 'user1@foo.bar', 'A1#dsa12'
    db = DBSession()
    user = prepare_user(db, username, email, password)
    prepare_comments(db, user)
    LOGGER.info('prepare data finished...')
    db.close()


def bootstrap():
    LOGGER.info('boostrap')
    dburl = db_engine.url
    if database_exists(dburl):
        drop_database(dburl)

    create_database(dburl)
    alembic_config = Config('alembic.ini')
    command.upgrade(alembic_config, 'head')
    command.history(alembic_config, indicate_current=True)
    prepare_data()


def teardown():
    dburl = db_engine.url
    if database_exists(dburl):
        drop_database(dburl)
