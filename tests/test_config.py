import os

from hera import Config


def test_config_contains_domain_host():
    host = "http://argo.com"
    config = Config(host=host, verify_ssl=False)
    assert config.config.host == host
    assert not config.config.verify_ssl
