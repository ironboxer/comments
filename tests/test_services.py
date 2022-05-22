import pytest

from comment.exceptions import (
    CommentReplyIdIncorrect,
    EmailAlreadyUsed,
    ObjectNotFound,
    UsernameAlreadyUsed,
    UsernameEmailCannotBothBeNone,
)


class TestAccountService:
    def test_register_with_repeat_username(self, db, account_service, user1):
        with pytest.raises(UsernameAlreadyUsed):
            account_service.register(user1.username, 'a@b.com', 'A21#ac')

    def test_register_with_repeat_email(self, db, account_service, user1):
        with pytest.raises(EmailAlreadyUsed):
            account_service.register('UUa231', user1.email, 'A2*dsdss')

    @pytest.mark.parametrize(
        'username,email,password',
        [
            ('Username1', 'user1@foo.bar', 'A1*24'),
        ],
    )
    def test_register(self, db, account_service, username, email, password):
        user = account_service.register(username, email, password)
        assert user.username == username
        assert user.email == email
        assert user.password_auth_provider.verify_secret(password)

    def test_login_without_username_and_password(self, account_service, password1):
        with pytest.raises(UsernameEmailCannotBothBeNone):
            account_service.login(password1, '', '')

    def test_login_with_incorrect_username(self, account_service, user1, password1):
        with pytest.raises(ObjectNotFound):
            account_service.login(password1, 'username-xxx', '')

    def test_login_with_incorrect_email(self, account_service, user1, password1):
        with pytest.raises(ObjectNotFound):
            account_service.login(password1, '', 'foo@bai.xom')

    @pytest.mark.parametrize(
        'username,email',
        [(pytest.lazy_fixture('username1'), ''), ('', pytest.lazy_fixture('email1'))],
    )
    def test_login(self, account_service, user1, password1, username, email):
        login_info = account_service.login(password1, username, email)
        assert login_info


class TestCommentService:
    def test_list(self, comment_service, comment1):
        comments = comment_service.list()
        assert len(comments) == 1
        assert comments[0].id == comment1.id

    def test_list_by_order(self, comment_service, comments_10):
        comments = comment_service.list()
        assert comments[::-1] == comments_10

    def test_create(self, comment_service, user1, content1):
        comment = comment_service.create(user1, content1)
        assert comment.content == content1

    def test_create_with_incorrect_reply_id(self, comment_service, user1, content1):
        with pytest.raises(CommentReplyIdIncorrect):
            comment_service.create(user1, content1, 12345)
