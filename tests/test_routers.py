import pytest
from starlette import status


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
