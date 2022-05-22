import arrow
import pytest

from comment.auth import OAuthScope
from comment.models import Account, AuthProvider, AuthProviderType, Comment
from comment.security import decode_jwt


class TestAccount:
    def test_create(self, db, username1, email1):
        _id = Account.create(db, id=1, username=username1, email=email1).id
        user = Account.get_by_id(db, _id)
        assert user.username == username1
        assert user.email == email1
        assert user.created_at
        assert user.updated_at

    def test_update(self, db, user1):
        with pytest.raises(NotImplementedError):
            user1.update(username='user123')

    def test_list(self, db, user1):
        users = Account.list(db).all()
        assert len(users) == 1

    def test_delete(self, db, user1):
        with pytest.raises(NotImplementedError):
            user1.delete()


class TestComment:
    def test_create(self, db, user1, content1):
        _id = Comment.create(
            db,
            account_id=user1.id,
            content=content1,
            user_info={'id': user1.id, 'username': user1.username},
        ).id
        comment = Comment.get_by_id(db, _id)
        assert comment.content == content1

    def test_update(self, db, comment1):
        with pytest.raises(NotImplementedError):
            comment1.update(content='world')

    def test_delete(self, db, comment1):
        with pytest.raises(NotImplementedError):
            comment1.delete()

    def test_list(self, db, comment1):
        comments = list(Comment.list(db))
        assert len(comments) == 1


class TestAuthProvider:
    def test_create_oauth_token(self, db, user1):
        provider, _ = AuthProvider.get_or_create(db, AuthProviderType.PASSWORD, user1)
        now = arrow.utcnow().shift(minutes=1)
        token = provider.create_oauth_token(
            expire_at=now.datetime, scopes=[OAuthScope.ME]
        )
        assert decode_jwt(token['access_token']) == {
            'sub': str(provider.account_id),
            'exp': now.int_timestamp,
            'scopes': [OAuthScope.ME],
        }
        assert token['expire_at'] == now.datetime
        assert token['user_id'] == provider.account_id
