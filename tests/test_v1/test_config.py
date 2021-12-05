import os

from hera.v1.config import Config


def test_config_contains_env_host():
    mock_address = 'address'
    mock_port = 'port'
    os.environ.setdefault('ARGO_SERVER_PORT_2746_TCP_ADDR', mock_address)
    os.environ.setdefault('ARGO_SERVER_PORT_2746_TCP_PORT', mock_port)

    expected_addr = 'http://address:port'

    config = Config('', verify=False)
    assert config.config.host == expected_addr
    assert not config.config.verify_ssl

    # deleting env vars since it influences the session and other tests
    del os.environ['ARGO_SERVER_PORT_2746_TCP_ADDR']
    del os.environ['ARGO_SERVER_PORT_2746_TCP_PORT']


def test_config_contains_domain_host():
    mock_domain = 'domain.com'

    expected_addr = 'https://domain.com'

    config = Config(mock_domain)
    assert config.config.host == expected_addr
    assert config.config.verify_ssl
