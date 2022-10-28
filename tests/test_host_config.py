import pytest

from hera import (
    Client,
    Config,
    get_global_api_version,
    get_global_host,
    get_global_namespace,
    get_global_service_account_name,
    get_global_token,
    get_global_verify_ssl,
    set_global_api_version,
    set_global_host,
    set_global_namespace,
    set_global_service_account_name,
    set_global_token,
    set_global_verify_ssl,
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


def test_global_verify_ssl_sets_as_expected():
    assert get_global_verify_ssl()
    set_global_verify_ssl(False)
    assert not get_global_verify_ssl()
    set_global_verify_ssl(True)
    assert get_global_verify_ssl()


def test_global_api_version_set_as_expected():
    assert get_global_api_version() == "argoproj.io/v1alpha1"
    set_global_api_version("testing_api_version")
    assert get_global_api_version() == "testing_api_version"
    set_global_api_version("argoproj.io/v1alpha1")
    assert get_global_api_version() == "argoproj.io/v1alpha1"


def test_global_service_account_name_set_as_expected():
    assert get_global_service_account_name() is None
    set_global_service_account_name("sa")
    assert get_global_service_account_name() == "sa"
    set_global_service_account_name(None)
    assert get_global_service_account_name() is None

def test_global_api_version_set_as_expected():
    assert get_global_api_version() == "argoproj.io/v1alpha1"
    set_global_api_version("testing_api_version")
    assert get_global_api_version() == "testing_api_version"
    set_global_api_version("argoproj.io/v1alpha1")
    assert get_global_api_version() == "argoproj.io/v1alpha1"
