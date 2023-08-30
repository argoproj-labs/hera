import os
from pathlib import Path
from shutil import rmtree

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


@pytest.fixture
def tmp_path_fixture():
    # create a temporary directory
    path = Path("test_outputs")
    path.mkdir(exist_ok=True)
    yield path
    # destroy the directory
    rmtree(path)
