import pytest
from starlette import status

from comment.exceptions import ErrorCode
from comment.schemas import CommentResp
from comment.utils.time import time_2_iso_format


def test_health(client):
    resp = client.get('/healthz')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.text == ''


def test_index(client):
    resp = client.get('/')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers.get('content-type') == 'text/html; charset=utf-8'
    assert resp.text


def test_register(mocker, client, username1, email1, password1):
    payload = {'username': username1, 'email': email1, 'password': password1}
    resp = client.post('/register', json=payload)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data == {
        'id': mocker.ANY,
        'created_at': mocker.ANY,
        'username': username1,
        'email': email1,
    }


@pytest.mark.parametrize(
    'password',
    [
        'UPPERCASE',
        'lowercase',
        '12345678',
        'AaBbCcDd',
        'A1B2C3D4',
        'a1b2c3d4',
        '!@#$%^&*',
        'AAAAAAA!',
        'aaaaaaa@',
        '1234567#',
    ],
)
def test_register_with_invalid_password_format(client, username1, email1, password):
    payload = {'username': username1, 'email': email1, 'password': password}
    resp = client.post('/register', json=payload)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    data = resp.json()
    assert data['code'] == ErrorCode.password_invalid_format


@pytest.mark.parametrize(
    'username,email',
    [
        (pytest.lazy_fixture('username1'), ''),
        ('', pytest.lazy_fixture('email1')),
    ],
)
def test_login(mocker, client, user1, password1, username, email):
    payload = {'password': password1}
    if username:
        payload['username'] = username
    elif email:
        payload['email'] = email

    resp = client.post('/login', json=payload)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data == {
        'user_id': user1.id,
        'access_token': mocker.ANY,
        'token_type': 'Bearer',
        'expire_at': mocker.ANY,
    }


def test_user(authed_client, user1):
    resp = authed_client.get('/user')
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data == {
        'id': user1.id,
        'username': user1.username,
        'email': user1.email,
        'created_at': time_2_iso_format(user1.created_at),
    }


def test_user_without_auth(client, user1):
    resp = client.get('/user')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestComment:
    def test_list(self, client, comment1):
        resp = client.get('/comments')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data) == 1
        assert data == [
            {
                'id': comment1.id,
                'reply_id': comment1.reply_id,
                'content': comment1.content,
                'created_at': time_2_iso_format(comment1.created_at),
                'user_info': {
                    'id': comment1.account.id,
                    'username': comment1.account.username,
                },
                'sub_comments': [],
            }
        ]

    def test_list_multi_comments(self, client, comments_10):
        resp = client.get('/comments')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data) == len(comments_10)
        for a, b in zip(data, comments_10[::-1]):
            assert a == CommentResp.serialize(b)

    @pytest.mark.parametrize(
        'content',
        [
            'hello',
            'wonderful',
            'give me a like',
        ],
    )
    def test_create(self, mocker, authed_client, user1, content):
        resp = authed_client.post('/comments', json={'content': content})
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data == {
            'id': mocker.ANY,
            'content': content,
            'reply_id': None,
            'created_at': mocker.ANY,
            'user_info': {
                'id': user1.id,
                'username': user1.username,
            },
            'sub_comments': [],
        }

    def test_create_without_auth(self, client):
        resp = client.post('/comments', json={'content': 'hello'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_mass_comments(self, client, comments_10k):
        # performance test
        resp = client.get('/comments')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data) == len(comments_10k)
