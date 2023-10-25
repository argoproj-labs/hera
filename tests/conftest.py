import os

import pytest

from hera.shared import global_config


@pytest.fixture
def global_config_fixture():
    global_config.reset()
    yield global_config
    global_config.reset()


@pytest.fixture
def environ_annotations_fixture():
    os.environ["hera__script_annotations"] = ""
    yield
    del os.environ["hera__script_annotations"]
