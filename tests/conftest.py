import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.testclient import TestClient

from alembic import command
from alembic.config import Config
from comment.db import engine as db_engine
from comment.db import get_db
from comment.main import app
from comment.models import Account, AuthProvider, AuthProviderType, Comment
from comment.security import get_password_hash
from comment.services import AccountService, CommentService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope='session')
def database_engine():
    # some implementation problem: alembic config has 'sqlalchemy.url'
    # point to URL in settings, this must be mocked before
    # sqlalchemy-utils do database migrations
    dburl = db_engine.url
    if database_exists(dburl):
        drop_database(dburl)
    create_database(dburl)
    alembic_config = Config('alembic.ini')
    command.upgrade(alembic_config, 'head')
    command.history(alembic_config, indicate_current=True)

    try:
        yield db_engine
    finally:
        command.downgrade(alembic_config, 'base')
        drop_database(dburl)


@pytest.fixture()
def db(database_engine):
    # https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    connection = database_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, 'after_transaction_end')
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def override_deps(db):
    app.dependency_overrides[get_db] = lambda: db


@pytest.fixture
def password1():
    return 'A1@abcdef'


@pytest.fixture
def email1():
    return 'foo@bar.com'


@pytest.fixture
def username1():
    return 'Username1'


@pytest.fixture
def user1(db, username1, email1, password1):
    account = Account.create(db, id=1, username=username1, email=email1)
    AuthProvider.create(
        db,
        id=1,
        auth_type=AuthProviderType.PASSWORD,
        account_id=account.id,
        hashed_secret=get_password_hash(password1),
    )
    return account


@pytest.fixture
def content1():
    return 'comment 1'


@pytest.fixture
def comment1(db, user1, content1):
    return Comment.create(db, account_id=user1.id, content=content1)


@pytest.fixture
def comments_10(db, user1):
    comments = [
        Comment.create(db, account_id=user1.id, content=f'comment {i}')
        for i in range(10)
    ]
    return comments


@pytest.fixture
def account_service(db):
    return AccountService(db)


@pytest.fixture
def comment_service(db):
    return CommentService(db)
