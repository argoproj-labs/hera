import pytest
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Outputs,
    IoArgoprojWorkflowV1alpha1ValueFrom,
)

from hera import Artifact, Parameter
from hera.io import IO


class TestIO:
    def test_build_inputs_returns_expected_inputs(self):
        io = IO(inputs=[Parameter("a"), Artifact("b", "/b")], outputs=[])
        inputs = io._build_inputs()
        assert isinstance(inputs, IoArgoprojWorkflowV1alpha1Inputs)
        assert hasattr(inputs, "parameters")
        assert len(inputs.parameters) == 1
        assert hasattr(inputs.parameters[0], "name")
        assert inputs.parameters[0].name == "a"

        assert hasattr(inputs, "artifacts")
        assert len(inputs.artifacts) == 1
        assert hasattr(inputs.artifacts[0], "name")
        assert hasattr(inputs.artifacts[0], "path")
        assert inputs.artifacts[0].name == "b"
        assert inputs.artifacts[0].path == "/b"

    def test_build_inputs_returns_none_on_no_input(self):
        io = IO(inputs=[], outputs=[])
        assert io._build_inputs() is None

    def test_build_outputs_returns_expected_outputs(self):
        io = IO(inputs=[], outputs=[Parameter("a", value="42"), Artifact("b", "/b")])
        outputs = io._build_outputs()
        assert isinstance(outputs, IoArgoprojWorkflowV1alpha1Outputs)
        assert hasattr(outputs, "parameters")
        assert len(outputs.parameters) == 1
        assert hasattr(outputs.parameters[0], "name")
        assert hasattr(outputs.parameters[0], "value_from")
        assert outputs.parameters[0].name == "a"
        assert isinstance(outputs.parameters[0].value_from, IoArgoprojWorkflowV1alpha1ValueFrom)
        assert hasattr(outputs.parameters[0].value_from, "parameter")
        assert outputs.parameters[0].value_from.parameter == "42"

        assert hasattr(outputs, "artifacts")
        assert len(outputs.artifacts) == 1
        assert hasattr(outputs.artifacts[0], "name")
        assert hasattr(outputs.artifacts[0], "path")
        assert outputs.artifacts[0].name == "b"
        assert outputs.artifacts[0].path == "/b"

    def test_build_outputs_returns_none_on_no_input(self):
        io = IO(inputs=[], outputs=[])
        assert io._build_outputs() is None

    def test_validate_io(self):
        with pytest.raises(AssertionError) as e:
            IO(inputs=[Parameter("a"), Parameter("a")], outputs=[])
            assert str(e.value) == "input parameters must have unique names"
        with pytest.raises(AssertionError) as e:
            IO(inputs=[Artifact("a", "/a"), Artifact("a", "/a")], outputs=[])
            assert str(e.value) == "input artifacts mut have unique names"
        with pytest.raises(AssertionError) as e:
            IO(inputs=[], outputs=[Parameter("a", value="42"), Parameter("a", value="42")])
            assert str(e.value) == "output parameters must have unique names"
        with pytest.raises(AssertionError) as e:
            IO(inputs=[], outputs=[Artifact("a", path="/a"), Artifact("a", path="/a")])
            assert str(e.value) == "output artifacts must have unique names"
