import pytest

from hera import set_global_host, set_global_token, Client, Config


def test_config_assembles_host_from_global_host():
    set_global_host('http://localhost:2746')
    config = Config().config
    assert config.host == 'http://localhost:2746'
    set_global_host(None)


def test_config_fails_when_no_host_is_provided():
    with pytest.raises(AssertionError) as e:
        Config()
    assert str(e.value) == 'A configuration/service host is required for submitting workflows'


def test_client_uses_global_token():
    set_global_host('http://localhost:2746')
    set_global_token('token')
    client = Client(Config())
    assert client.api_client.default_headers['Authorization'] == 'Bearer token'
    set_global_token(None)
    set_global_host(None)
