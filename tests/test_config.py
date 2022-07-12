import os

from hera import Config


def test_config_contains_env_host():
    mock_address = "address"
    mock_port = "port"
    os.environ.setdefault("ARGO_SERVER_PORT_2746_TCP_ADDR", mock_address)
    os.environ.setdefault("ARGO_SERVER_PORT_2746_TCP_PORT", mock_port)

    expected_addr = "https://address:port"

    config = Config()
    assert config.config.host == expected_addr
    assert config.config.verify_ssl

    # deleting env vars since it influences the session and other tests
    del os.environ["ARGO_SERVER_PORT_2746_TCP_ADDR"]
    del os.environ["ARGO_SERVER_PORT_2746_TCP_PORT"]


def test_config_contains_domain_host():
    host = "http://argo.com"
    config = Config(host=host, verify_ssl=False)
    assert config.config.host == host
    assert not config.config.verify_ssl
