import pytest

from hera.workflows import Env, Parameter, Workflow
from hera.workflows._mixins import ArgumentsMixin, ContainerMixin, EnvMixin, IOMixin
from hera.workflows.models import (
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
    ImagePullPolicy,
    Inputs as ModelInputs,
    Outputs as ModelOutputs,
    Parameter as ModelParameter,
)


class TestContainerMixin:
    def test_build_image_pull_policy(self) -> None:
        assert ContainerMixin(image_pull_policy="Always")._build_image_pull_policy() == ImagePullPolicy.always.value
        assert (
            ContainerMixin(image_pull_policy=ImagePullPolicy.always)._build_image_pull_policy()
            == ImagePullPolicy.always.value
        )
        assert ContainerMixin()._build_image_pull_policy() is None


class TestIOMixin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.io_mixin = IOMixin()

    def test_get_parameter_success(self):
        self.io_mixin.inputs = Parameter(name="test", value="value")
        param = self.io_mixin.get_parameter("test")
        assert param.name == "test"
        assert param.value == "{{inputs.parameters.test}}"

    def test_get_model_parameter_success(self):
        self.io_mixin.inputs = ModelParameter(name="test", value="value")
        param = self.io_mixin.get_parameter("test")
        assert param.name == "test"
        assert param.value == "{{inputs.parameters.test}}"

    def test_get_parameter_no_inputs(self):
        with pytest.raises(KeyError):
            self.io_mixin.get_parameter("test")

    def test_get_parameter_no_parameters(self):
        self.io_mixin.inputs = ModelInputs()
        with pytest.raises(KeyError):
            self.io_mixin.get_parameter("test")

    def test_get_parameter_not_found(self):
        self.io_mixin.inputs = Parameter(name="test", value="value")
        with pytest.raises(KeyError):
            self.io_mixin.get_parameter("not_exist")

    def test_get_artifact_success(self):
        self.io_mixin.inputs = ModelInputs(artifacts=[ModelArtifact(name="test")])
        artifact = self.io_mixin.get_artifact("test")
        assert artifact.name == "test"
        assert artifact.from_ == "{{inputs.artifacts.test}}"

    def test_get_artifact_no_inputs(self):
        with pytest.raises(KeyError):
            self.io_mixin.get_artifact("test")

    def test_get_artifact_no_artifacts(self):
        self.io_mixin.inputs = ModelInputs()
        with pytest.raises(KeyError):
            self.io_mixin.get_artifact("test")

    def test_get_artifact_not_found(self):
        self.io_mixin.inputs = ModelInputs(artifacts=[ModelArtifact(name="test")])
        with pytest.raises(KeyError):
            self.io_mixin.get_artifact("not_exist")

    def test_build_inputs_none(self):
        assert self.io_mixin._build_inputs() is None

    def test_build_inputs_from_model_inputs_with_hera_parameter(self):
        # We must rebuild Parameter otherwise it will extra fields (output) that are not in ModelParameter
        self.io_mixin.inputs = ModelInputs(parameters=[Parameter(name="test", value="value")])
        assert self.io_mixin._build_inputs() == ModelInputs(parameters=[ModelParameter(name="test", value="value")])

    def test_build_outputs_none(self):
        assert self.io_mixin._build_outputs() is None

    def test_build_outputs_artifact_success(self):
        self.io_mixin.outputs = ModelOutputs(artifacts=[ModelArtifact(name="test")])
        built_outputs = self.io_mixin._build_outputs()
        assert built_outputs and built_outputs.artifacts == [ModelArtifact(name="test")]

    def test_build_outputs_of_parameter_converted(self):
        self.io_mixin.outputs = ModelOutputs(parameters=[Parameter(name="my-param-1")])
        built_outputs = self.io_mixin._build_outputs()
        assert built_outputs and built_outputs.parameters == [ModelParameter(name="my-param-1")]


class TestArgumentsMixin:
    def test_list_normalized_to_list(self):
        args_mixin = ArgumentsMixin(
            arguments=[
                Parameter(name="my-param-1"),
                Parameter(name="my-param-2"),
            ]
        )

        assert isinstance(args_mixin.arguments, list)
        assert len(args_mixin.arguments) == 2

    def test_single_value_normalized_to_list(self):
        args_mixin = ArgumentsMixin(arguments=Parameter(name="my-param"))

        assert isinstance(args_mixin.arguments, list)
        assert len(args_mixin.arguments) == 1

    def test_none_value_is_not_normalized_to_list(self):
        args_mixin = ArgumentsMixin(arguments=None)

        assert args_mixin.arguments is None

    def test_model_arguments_value_is_not_normalized_to_list(self):
        args_mixin = ArgumentsMixin(arguments=ModelArguments())

        assert args_mixin.arguments == ModelArguments()

    def test_build_arguments_of_parameter_converted(self):
        args_mixin = ArgumentsMixin(arguments=[Parameter(name="my-param-1")])
        built_args = args_mixin._build_arguments()
        assert built_args and built_args.parameters == [ModelParameter(name="my-param-1")]

    def test_build_workflow(self):
        with Workflow(
            name="test",
            arguments=ModelArguments(parameters=[Parameter(name="test", value="value")]),
        ) as w:
            pass

        workflow = w.build()
        assert workflow.spec.arguments.parameters == [ModelParameter(name="test", value="value")]


class TestEnvMixin:
    def test_list_normalized_to_list(self):
        env_mixin = EnvMixin(
            env=[
                Env(name="test-1", value="test"),
                Env(name="test-2", value="test"),
            ]
        )

        assert isinstance(env_mixin.env, list)
        assert len(env_mixin.env) == 2

    def test_single_value_normalized_to_list(self):
        env_mixin = EnvMixin(env=Env(name="test", value="test"))

        assert isinstance(env_mixin.env, list)
        assert len(env_mixin.env) == 1

    def test_none_value_is_not_normalized_to_list(self):
        env_mixin = EnvMixin(env=None)

        assert env_mixin.env is None
