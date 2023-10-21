import importlib

from hera.workflows import Workflow, script
from hera.workflows.script import _get_inputs_from_callable


def test_get_inputs_from_callable_simple_params():
    # GIVEN
    entrypoint = "tests.helper:my_function"
    module, function_name = entrypoint.split(":")
    function = getattr(importlib.import_module(module), function_name)

    # WHEN
    params, artifacts = _get_inputs_from_callable(function)

    # THEN
    assert params is not None
    assert artifacts == []

    assert isinstance(params, list)
    assert len(params) == 2
    a = params[0]
    b = params[1]

    assert a.name == "a"
    assert b.name == "b"


def test_get_inputs_from_callable_no_params():
    # GIVEN
    entrypoint = "tests.helper:no_param_function"
    module, function_name = entrypoint.split(":")
    function = getattr(importlib.import_module(module), function_name)

    # WHEN
    params, artifacts = _get_inputs_from_callable(function)

    # THEN
    assert params == []
    assert artifacts == []


def test_get_inputs_from_callable_simple_artifact(tmp_path, monkeypatch):
    # GIVEN
    if not tmp_path.is_file():
        tmp_path = tmp_path / "my_file.txt"

    tmp_path.touch()
    tmp_path.write_text("Hello there")
    import tests.helper as test_module

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))

    entrypoint = "tests.script_annotations.artifact_inputs:no_loader"
    module, function_name = entrypoint.split(":")
    md = importlib.import_module(module)
    importlib.reload(md)
    function = getattr(md, function_name)

    # WHEN
    params, artifacts = _get_inputs_from_callable(function)

    # THEN
    assert params == []
    assert artifacts is not None

    assert isinstance(artifacts, list)
    assert len(artifacts) == 1
    an_artifact = artifacts[0]

    assert an_artifact.name == "my-artifact"
    assert an_artifact.path == str(tmp_path)


@script(name="my-alt-name")
def my_func():
    print("Hello world!")


def test_script_name_kwarg_in_decorator():
    # GIVEN my_func above
    # WHEN
    with Workflow(name="test-script") as w:
        my_func()

    # THEN
    assert w.templates[0].name == "my-alt-name"


def test_script_parses_static_method():
    class Test:
        @script()
        @staticmethod
        def my_func():
            print(42)

        @script(name="test")
        @staticmethod
        def my_func2():
            print(42)

    # GIVEN my_func above
    # WHEN
    with Workflow(name="test-script") as w:
        Test.my_func()
        Test.my_func2()

    # THEN
    assert len(w.templates) == 2
    assert w.templates[0].name == "my-func"
    assert w.templates[1].name == "test"
