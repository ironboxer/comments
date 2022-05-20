from starlette import status


def test_health(client):
    resp = client.get('/healthz')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.text == ''
