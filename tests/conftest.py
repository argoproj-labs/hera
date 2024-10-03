import pytest

from hera.shared import global_config
from hera.workflows._context import _context


@pytest.fixture
def global_config_fixture():
    global_config.reset()
    yield global_config
    global_config.reset()


@pytest.fixture(autouse=True)
def clear_context():
    _context.declaring = False
