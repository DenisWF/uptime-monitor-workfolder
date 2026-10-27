import httpx

from app.checker import check_url


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_success():
    client = make_client(lambda req: httpx.Response(200))
    result = check_url("http://test.local", client=client)
    assert result.is_up is True
    assert result.status_code == 200
    assert result.error is None


def test_server_error_is_down():
    client = make_client(lambda req: httpx.Response(500))
    result = check_url("http://test.local", client=client)
    assert result.is_up is False
    assert result.status_code == 500


def test_timeout_is_down():
    def handler(request):
        raise httpx.ConnectTimeout("timed out", request=request)

    result = check_url("http://test.local", client=make_client(handler))
    assert result.is_up is False
    assert result.status_code is None
    assert "ConnectTimeout" in result.error


def test_connection_error_is_down():
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    result = check_url("http://test.local", client=make_client(handler))
    assert result.is_up is False
    assert "ConnectError" in result.error