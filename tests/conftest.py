import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.testclient import TestClient

from alembic import command
from alembic.config import Config
from comment.auth import OAuthScope
from comment.db import engine as db_engine
from comment.db import get_db
from comment.main import app
from comment.models import Account, AuthProvider, AuthProviderType, Comment
from comment.schemas import UserInfo
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
def account_service(db):
    return AccountService(db)


@pytest.fixture
def comment_service(db):
    return CommentService(db)


@pytest.fixture
def password1():
    return 'A1@abcdef'


@pytest.fixture
def password2():
    return 'B2$diau3'


@pytest.fixture
def email1():
    return 'user1@foo.bar'


@pytest.fixture
def email2():
    return 'user2@foo.bar'


@pytest.fixture
def username1():
    return 'Username1'


@pytest.fixture
def username2():
    return 'Username2'


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
def user2(db, username2, email2, password2):
    account = Account.create(db, id=2, username=username2, email=email2)
    AuthProvider.create(
        db,
        id=2,
        auth_type=AuthProviderType.PASSWORD,
        account_id=account.id,
        hashed_secret=get_password_hash(password2),
    )
    return account


@pytest.fixture
def content1():
    return 'comment 1'


@pytest.fixture
def content2():
    return 'comment 2'


@pytest.fixture
def comment1(comment_service, user1, content1):
    return comment_service.create(user1, content1)


@pytest.fixture
def comments_10(comment_service, user1):
    comments = [
        comment_service.create(user1, content=f'comment {i}') for i in range(10)
    ]
    return comments


@pytest.fixture
def comments_10k(db, user1):
    # for performance test
    comments = [
        {
            'content': f'content {i}',
            'account_id': user1.id,
            'user_info': UserInfo.serialize(user1),
        }
        for i in range(10_000)
    ]
    Comment.bulk_create(db, comments)
    return comments


@pytest.fixture
def comments_mass_nested(db, user1):
    """# noqa:D205
    [
        {
            'id': 1,
            'sub_comments: [
                {
                    'id': 2,
                    'sub_comments': [
                        {
                            'id': 3,
                            ...
                        }
                    ]
                }
            ]
        },
    ]
    """
    comments = [
        {
            'id': i,
            'reply_id': i - 1,
            'content': f'content {i}',
            'account_id': user1.id,
            'user_info': UserInfo.serialize(user1),
        }
        # Python>=3.9.6 maximum recursion depth == 995
        # Pydantic
        # RecursionError: maximum recursion depth exceeded while calling a Python object
        # Javascript Maximum call stack size exceed == 11387 Chrome (101.0.4951.5)
        # Uncaught RangeError: Maximum call stack size exceeded
        for i in range(1, 75 + 1)
    ]
    comments[0]['reply_id'] = None
    Comment.bulk_create(db, comments)
    return comments


@pytest.fixture
def access_token1(user1):
    return user1.password_auth_provider.create_oauth_token(scopes=[OAuthScope.ME])[
        'access_token'
    ]


@pytest.fixture
def authed_client(client, access_token1):
    client.headers['Authorization'] = f'Bearer {access_token1}'
    return client
