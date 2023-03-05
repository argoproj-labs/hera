import pytest
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Parameter,
    IoArgoprojWorkflowV1alpha1ValueFrom,
)

from hera.workflows.parameter import Parameter
from hera.workflows.value_from import ValueFrom


class TestParameter:
    def test_init_raises_value_error_using_value_and_value_from(self):
        with pytest.raises(ValueError) as e:
            Parameter("a", value_from=ValueFrom(default="42"), value="42")
        assert str(e.value) == "Cannot specify both `value` and `value_from` when instantiating `Parameter`"

    def test_as_name_returns_expected_parameter(self):
        p = Parameter("a", value="42").as_name("b")
        assert isinstance(p, Parameter)
        assert p.name == "b"

    def test_as_argument_returns_None_on_default_with_no_values(self):
        arg = Parameter("a", default="42").as_argument()
        assert arg is None

    def test_as_argument_returns_expected_parameter(self):
        arg = Parameter("a", value="42").as_argument()
        assert isinstance(arg, IoArgoprojWorkflowV1alpha1Parameter)
        assert hasattr(arg, "value")
        assert arg.value == "42"

        arg = Parameter("a", value_from=ValueFrom(path="abc")).as_argument()
        assert isinstance(arg, IoArgoprojWorkflowV1alpha1Parameter)
        assert hasattr(arg, "value_from")
        assert isinstance(arg.value_from, IoArgoprojWorkflowV1alpha1ValueFrom)
        assert hasattr(arg.value_from, "path")
        assert arg.value_from.path == "abc"

    def test_as_input_returns_expected_parameter(self):
        param = Parameter("a", default="42", enum=["42", "100"]).as_input()
        assert isinstance(param, IoArgoprojWorkflowV1alpha1Parameter)
        assert hasattr(param, "default")
        assert hasattr(param, "enum") and param.enum == ["42", "100"]
        assert param.default == "42"

    def test_as_output_returns_expected_parameter(self):
        param = Parameter("a", value_from=ValueFrom(path="abc")).as_output()
        assert isinstance(param, IoArgoprojWorkflowV1alpha1Parameter)
        assert hasattr(param, "name")
        assert param.name == "a"
        assert hasattr(param, "value_from")
        assert isinstance(param.value_from, IoArgoprojWorkflowV1alpha1ValueFrom)
        assert hasattr(param.value_from, "path")
        assert not hasattr(param.value_from, "default")
        assert not hasattr(param.value_from, "parameter")
        assert param.value_from.path == "abc"

        param = Parameter("a", value="43", default="42").as_output()
        assert isinstance(param, IoArgoprojWorkflowV1alpha1Parameter)
        assert hasattr(param, "name")
        assert param.name == "a"
        assert hasattr(param, "value_from")
        assert isinstance(param.value_from, IoArgoprojWorkflowV1alpha1ValueFrom)
        assert hasattr(param.value_from, "default")
        assert param.value_from.default == "42"
        assert hasattr(param.value_from, "parameter")
        assert param.value_from.parameter == "43"

    def test_str_returns_expected_string(self):
        assert str(Parameter("a", value="42")) == "42"

    def test_str_raises_value_error_on_no_value_set(self):
        with pytest.raises(ValueError) as e:
            str(Parameter("a"))
        assert str(e.value) == "Cannot represent `Parameter` as string as `value` is not set"

    def test_contains_items_returns_true_on_value_present(self):
        p = Parameter("a", value="{{item.a}}")
        assert p.contains_item

    def test_contains_value_returns_expected_false(self):
        p = Parameter("a", value="42")
        assert not p.contains_item

    def test_value_and_value_from_not_set_together(self):
        with pytest.raises(ValueError):
            Parameter("a", value="42", value_from=ValueFrom())

        p = Parameter("a", value="42")
        assert p.value_from is None
        assert p.value is not None

        p = Parameter("a", value_from=ValueFrom(path="/test"))
        assert p.value is None
        assert p.value_from is not None
        assert p.value_from.path == "/test"
