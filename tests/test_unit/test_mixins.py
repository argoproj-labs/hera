import pytest

from hera.workflows import Parameter
from hera.workflows._mixins import ContainerMixin, IOMixin
from hera.workflows.models import (
    ImagePullPolicy,
    Inputs as ModelInputs,
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
        self.io_mixin.inputs = ModelInputs(parameters=[Parameter(name="test", value="value")])
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
        self.io_mixin.inputs = ModelInputs(parameters=[Parameter(name="test", value="value")])
        with pytest.raises(KeyError):
            self.io_mixin.get_parameter("not_exist")

    def test_build_inputs_none(self):
        assert self.io_mixin._build_inputs() is None

    def test_build_inputs_from_model_inputs(self):
        model_inputs = ModelInputs(parameters=[Parameter(name="test", value="value")])
        self.io_mixin.inputs = model_inputs
        assert self.io_mixin._build_inputs() == model_inputs

    def test_build_outputs_none(self):
        assert self.io_mixin._build_outputs() is None
