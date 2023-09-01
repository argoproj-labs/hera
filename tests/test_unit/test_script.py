import importlib

from hera.workflows import script
from hera.workflows.script import _get_parameters_and_artifacts_from_callable
from hera.workflows.workflow import Workflow


def test_get_parameters_and_artifacts_from_callable_simple_params():
    # GIVEN
    entrypoint = "tests.helper:my_function"
    module, function_name = entrypoint.split(":")
    function = getattr(importlib.import_module(module), function_name)

    # WHEN
    params, artifacts = _get_parameters_and_artifacts_from_callable(function)

    # THEN
    assert params is not None
    assert artifacts == []

    assert isinstance(params, list)
    assert len(params) == 2
    a = params[0]
    b = params[1]

    assert a.name == "a"
    assert b.name == "b"


def test_get_parameters_and_artifacts_from_callable_no_params():
    # GIVEN
    entrypoint = "tests.helper:no_param_function"
    module, function_name = entrypoint.split(":")
    function = getattr(importlib.import_module(module), function_name)

    # WHEN
    params, artifacts = _get_parameters_and_artifacts_from_callable(function)

    # THEN
    assert params == []
    assert artifacts == []


def test_get_parameters_and_artifacts_from_callable_simple_artifact(tmp_path, monkeypatch):
    # GIVEN
    if not tmp_path.is_file():
        tmp_path = tmp_path / "my_file.txt"

    tmp_path.touch()
    tmp_path.write_text("Hello there")
    import tests.helper as test_module

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))

    entrypoint = "tests.script_annotations_artifacts.script_annotations_artifact_path:read_artifact"
    module, function_name = entrypoint.split(":")
    md = importlib.import_module(module)
    importlib.reload(md)
    function = getattr(md, function_name)

    # WHEN
    params, artifacts = _get_parameters_and_artifacts_from_callable(function)

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
