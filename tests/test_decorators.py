import importlib
import logging


def test_set_entrypoint():
    w = importlib.import_module("tests.workflow_decorators.set_entrypoint").w

    assert w.entrypoint == "goodbye-world"


def test_multiple_set_entrypoint(caplog):
    with caplog.at_level(logging.WARNING):
        w = importlib.import_module("tests.workflow_decorators.multiple_entrypoints").w

    assert "entrypoint is being reassigned" in caplog.text
    assert w.entrypoint == "hello-world-2"
