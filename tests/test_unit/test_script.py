from pathlib import Path
from typing import Annotated, Dict, List, Optional, Union, cast

import pytest

from hera.shared._global_config import _GlobalConfig
from hera.workflows._mixins import EnvT
from hera.workflows.artifact import Artifact
from hera.workflows.env import Env
from hera.workflows.io import Output
from hera.workflows.models import (
    EnvVar as ModelEnvVar,
    ScriptTemplate,
    Workflow as ModelWorkflow,
)
from hera.workflows.parameter import Parameter
from hera.workflows.script import (
    RunnerScriptConstructor,
    _get_inputs_from_callable,
    _get_outputs_from_return_annotation,
    script,
)
from hera.workflows.workflow import Workflow


def test_get_inputs_from_callable_simple_params():
    # GIVEN
    def my_function(a: int, b: str):
        return a + b

    # WHEN
    params, artifacts = _get_inputs_from_callable(my_function)

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
    def no_param_function():
        return "Hello there!"

    # WHEN
    params, artifacts = _get_inputs_from_callable(no_param_function)

    # THEN
    assert params == []
    assert artifacts == []


def test_get_artifact_input():
    # GIVEN
    def input_artifact_function(an_artifact: Annotated[Path, Artifact(name="my-artifact", path="my-file.txt")]) -> str:
        return an_artifact.read_text()

    # WHEN
    params, artifacts = _get_inputs_from_callable(input_artifact_function)

    # THEN
    assert params == []
    assert isinstance(artifacts, list)
    assert len(artifacts) == 1
    an_artifact = artifacts[0]

    assert an_artifact.name == "my-artifact"
    assert an_artifact.path == "my-file.txt"


def test_script_name_kwarg_in_decorator():
    # GIVEN
    @script(name="my-alt-name")
    def my_func():
        print("Hello world!")

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


def test_script_ignores_unknown_annotations():
    # GIVEN
    @script()
    def unknown_annotations_ignored(my_string: Annotated[str, "some metadata"]) -> str:
        return my_string

    # WHEN
    params, artifacts = _get_inputs_from_callable(unknown_annotations_ignored)

    # THEN
    assert artifacts == []
    assert isinstance(params, list)
    assert len(params) == 1
    parameter = params[0]

    assert parameter.name == "my_string"
    assert parameter.default is None


def test_script_optional_parameter():
    # GIVEN
    @script()
    def unknown_annotations_ignored(my_optional_string: Optional[str] = None) -> str:
        return "Got: {}".format(my_optional_string)

    # WHEN
    params, artifacts = _get_inputs_from_callable(unknown_annotations_ignored)

    # THEN
    assert artifacts == []
    assert isinstance(params, list)
    assert len(params) == 1
    parameter = params[0]

    assert parameter.name == "my_optional_string"
    assert parameter.default == "null"


def test_invalid_script_when_optional_parameter_does_not_have_default_value():
    @script()
    def unknown_annotations_ignored(my_optional_string: Optional[str]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' must have a default value of None."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_2():
    @script()
    def unknown_annotations_ignored(my_optional_string: Annotated[Optional[str], "123"]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' must have a default value of None."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_3():
    @script()
    def unknown_annotations_ignored(my_optional_string: Union[str, None]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' must have a default value of None."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_4():
    @script()
    def unknown_annotations_ignored(my_optional_string: Union[None, str]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' must have a default value of None."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_5():
    @script()
    def unknown_annotations_ignored(my_optional_string: Optional[str] = "123") -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' must have a default value of None."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_6():
    @script()
    def unknown_annotations_ignored(my_optional_string: Annotated[Optional[str], Parameter(name="my-string")]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' must have a default value of None."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_multiple_input_workflow_annotations_are_given():
    @script()
    def invalid_script(a_str: Annotated[str, Artifact(name="a_str"), Parameter(name="a_str")] = "123") -> str:
        return "Got: {}".format(a_str)

    with pytest.raises(ValueError, match="Annotation metadata cannot contain more than one Artifact/Parameter."):
        _get_inputs_from_callable(invalid_script)


def test_script_returning_generic():
    @script()
    def valid_script(a_str: str = "123") -> Dict[str, str]:
        return {"input": a_str}

    result = _get_outputs_from_return_annotation(valid_script, None)

    assert result == ([], [])


def test_script_returning_annotated_generic():
    @script()
    def valid_script(a_str: str = "123") -> Annotated[Dict[str, str], Artifact(name="an_artifact")]:
        return {"input": a_str}

    result = _get_outputs_from_return_annotation(valid_script, None)

    assert result == ([], [Artifact(name="an_artifact")])


def test_script_returning_pydantic_type(global_config_fixture):
    global_config_fixture.experimental_features["script_pydantic_io"] = True

    class MyOutput(Output):
        foo: str
        bar: int

    @script()
    def valid_script(a_str: str = "123") -> MyOutput:
        return MyOutput(foo=a_str, bar=int(a_str))

    result = _get_outputs_from_return_annotation(valid_script, None)

    assert result == ([Parameter(name="foo"), Parameter(name="bar")], [])


def test_invalid_script_when_multiple_output_workflow_annotations_are_given():
    @script()
    def invalid_script(a_str: str = "123") -> Annotated[str, Artifact(name="a_str"), Artifact(name="b_str")]:
        return "Got: {}".format(a_str)

    with pytest.raises(ValueError, match="Annotation metadata cannot contain more than one Artifact/Parameter."):
        _get_outputs_from_return_annotation(invalid_script, None)


class TestRunnerScriptEnv:
    @staticmethod
    def build_workflow(script_env, constructor=None) -> ModelWorkflow:
        constructor = constructor if constructor is not None else RunnerScriptConstructor()

        @script(constructor=constructor, env=script_env)
        def my_script():
            pass

        with Workflow(name="test") as w:
            my_script()

        return cast(ModelWorkflow, w.build())

    @pytest.mark.parametrize(
        "user_env,expected_env",
        (
            [
                None,
                None,
            ],
            [
                Env(name="my_env_var", value=42),
                [ModelEnvVar(name="my_env_var", value=42)],
            ],
        ),
    )
    def test_runner_script_no_added_env_vars(self, user_env: EnvT, expected_env):
        built_workflow = self.build_workflow(user_env)

        script_template = cast(ScriptTemplate, built_workflow.spec.templates[0].script)
        assert script_template is not None
        assert script_template.env == expected_env

    @pytest.mark.parametrize(
        "user_env,expected_env",
        (
            [
                None,
                [
                    ModelEnvVar(name="hera__outputs_directory", value="/my/tmp/dir"),
                ],
            ],
            [
                Env(name="my_env_var", value=42),
                [
                    ModelEnvVar(name="my_env_var", value=42),
                    ModelEnvVar(name="hera__outputs_directory", value="/my/tmp/dir"),
                ],
            ],
        ),
    )
    def test_runner_script_output_dir_env_var(self, user_env: EnvT, expected_env: Optional[List[ModelEnvVar]]):
        # GIVEN
        constructor = RunnerScriptConstructor(outputs_directory="/my/tmp/dir")

        built_workflow = self.build_workflow(user_env, constructor)

        script_template = cast(ScriptTemplate, built_workflow.spec.templates[0].script)
        assert script_template is not None
        assert script_template.env == expected_env

    @pytest.mark.parametrize(
        "user_env,expected_env",
        (
            [
                None,
                [
                    ModelEnvVar(name="hera__pydantic_mode", value="1"),
                ],
            ],
            [
                Env(name="my_env_var", value=42),
                [
                    ModelEnvVar(name="my_env_var", value=42),
                    ModelEnvVar(name="hera__pydantic_mode", value="1"),
                ],
            ],
        ),
    )
    def test_runner_script_pydantic_mode_env_var(self, user_env: EnvT, expected_env: Optional[List[ModelEnvVar]]):
        # GIVEN
        constructor = RunnerScriptConstructor(pydantic_mode=1)

        built_workflow = self.build_workflow(user_env, constructor)

        script_template = cast(ScriptTemplate, built_workflow.spec.templates[0].script)
        assert script_template is not None
        assert script_template.env == expected_env

    @pytest.mark.parametrize(
        "user_env,expected_env",
        (
            [
                None,
                [
                    ModelEnvVar(name="hera__script_pydantic_io", value=""),
                ],
            ],
            [
                Env(name="my_env_var", value=42),
                [
                    ModelEnvVar(name="my_env_var", value=42),
                    ModelEnvVar(name="hera__script_pydantic_io", value=""),
                ],
            ],
        ),
    )
    def test_runner_script_pydantic_io_env_var(
        self,
        global_config_fixture: _GlobalConfig,
        user_env: EnvT,
        expected_env: Optional[List[ModelEnvVar]],
    ):
        # GIVEN
        global_config_fixture.experimental_features["script_pydantic_io"] = True
        constructor = RunnerScriptConstructor()

        built_workflow = self.build_workflow(user_env, constructor)

        script_template = cast(ScriptTemplate, built_workflow.spec.templates[0].script)
        assert script_template is not None
        assert script_template.env == expected_env
