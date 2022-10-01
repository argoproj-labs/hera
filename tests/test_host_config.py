import pytest

from hera import (
    Client,
    Config,
    get_global_host,
    get_global_namespace,
    get_global_token,
    set_global_host,
    set_global_namespace,
    set_global_token,
)


def test_config_assembles_host_from_global_host():
    set_global_host("http://localhost:2746")
    config = Config().config
    assert config.host == "http://localhost:2746"
    set_global_host(None)


def test_config_fails_when_no_host_is_provided():
    with pytest.raises(AssertionError) as e:
        Config()
    assert str(e.value) == "A configuration/service host is required for submitting workflows"


@pytest.mark.parametrize(
    ["set_token"],
    [
        (lambda: set_global_token("token"),),
        (lambda: set_global_token(lambda: "token"),),
    ],
)
def test_client_uses_global_token(set_token):
    set_global_host("http://localhost:2746")
    set_token()
    client = Client(Config())
    assert client.api_client.default_headers["Authorization"] == "Bearer token"
    set_global_token(None)
    set_global_host(None)


def test_config_fails_when_no_token_is_provided():
    set_global_host("http://localhost:2746")
    with pytest.raises(AssertionError) as e:
        Client(Config())
    assert str(e.value) == "No token was provided and no global token was found."
    set_global_host(None)


def test_global_namespace_set_as_expected():
    assert get_global_namespace() == "default"
    set_global_namespace("argo")
    assert get_global_namespace() == "argo"
    set_global_namespace("default")
    assert get_global_namespace() == "default"


def test_global_host_set_as_expected():
    assert get_global_host() is None
    set_global_host("host")
    assert get_global_host() == "host"
    set_global_host(None)
    assert get_global_host() is None


def test_global_token_set_as_expected():
    assert get_global_token() is None
    set_global_token("token")
    assert get_global_token() == "token"
    set_global_token(None)
    assert get_global_token() is None
