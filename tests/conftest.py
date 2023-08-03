import pytest

from hera.shared import global_config


@pytest.fixture
def global_config_fixture():
    global_config.reset()
    yield global_config
    global_config.reset()
