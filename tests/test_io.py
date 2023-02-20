import pytest
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Outputs,
)

from hera.workflows import Artifact, Parameter
from hera.workflows.io import IO


class TestIO:
    def test_build_inputs_returns_expected_inputs(self):
        io = IO(inputs=[Artifact("b", "/b")])
        assert len(io.inputs) == 1
        assert isinstance(io.inputs[0], Artifact)
        inputs = io._build_inputs()
        assert hasattr(inputs, "artifacts")
        assert len(inputs.artifacts) == 1
        assert hasattr(inputs.artifacts[0], "name")
        assert hasattr(inputs.artifacts[0], "path")
        assert inputs.artifacts[0].name == "b"
        assert inputs.artifacts[0].path == "/b"

        io = IO(inputs=[Parameter("a")])
        assert len(io.inputs) == 1
        assert isinstance(io.inputs[0], Parameter)
        inputs = io._build_inputs()
        assert isinstance(inputs, IoArgoprojWorkflowV1alpha1Inputs)
        assert hasattr(inputs, "parameters")
        assert len(inputs.parameters) == 1
        assert hasattr(inputs.parameters[0], "name")
        assert inputs.parameters[0].name == "a"

        io = IO(inputs=[Artifact("b", "/b"), Parameter("a")])
        assert len(io.inputs) == 2
        assert isinstance(io.inputs[0], Artifact)
        assert isinstance(io.inputs[1], Parameter)
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
        io = IO(outputs=[Artifact("b", "/b")])
        assert len(io.outputs) == 1
        assert isinstance(io.outputs[0], Artifact)
        outputs = io._build_outputs()
        assert hasattr(outputs, "artifacts")
        assert len(outputs.artifacts) == 1
        assert hasattr(outputs.artifacts[0], "name")
        assert hasattr(outputs.artifacts[0], "path")
        assert outputs.artifacts[0].name == "b"
        assert outputs.artifacts[0].path == "/b"

        io = IO(outputs=[Parameter("a", value="a")])
        assert len(io.outputs) == 1
        assert isinstance(io.outputs[0], Parameter)
        outputs = io._build_outputs()
        assert isinstance(outputs, IoArgoprojWorkflowV1alpha1Outputs)
        assert hasattr(outputs, "parameters")
        assert len(outputs.parameters) == 1
        assert hasattr(outputs.parameters[0], "name")
        assert outputs.parameters[0].name == "a"

        io = IO(outputs=[Artifact("b", "/b"), Parameter("a", value="a")])
        assert len(io.outputs) == 2
        assert isinstance(io.outputs[0], Artifact)
        assert isinstance(io.outputs[1], Parameter)
        outputs = io._build_outputs()
        assert isinstance(outputs, IoArgoprojWorkflowV1alpha1Outputs)
        assert hasattr(outputs, "parameters")
        assert len(outputs.parameters) == 1
        assert hasattr(outputs.parameters[0], "name")
        assert outputs.parameters[0].name == "a"
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
            IO(inputs=[Parameter("a"), Parameter("a")], outputs=[])._validate_io()
        assert str(e.value) == "input parameters must have unique names"
        with pytest.raises(AssertionError) as e:
            IO(inputs=[Artifact("a", "/a"), Artifact("a", "/a")], outputs=[])._validate_io()
        assert str(e.value) == "input artifacts must have unique names"
        with pytest.raises(AssertionError) as e:
            IO(inputs=[], outputs=[Parameter("a", value="42"), Parameter("a", value="42")])._validate_io()
        assert str(e.value) == "output parameters must have unique names"
        with pytest.raises(AssertionError) as e:
            IO(inputs=[], outputs=[Artifact("a", path="/a"), Artifact("a", path="/a")])._validate_io()
        assert str(e.value) == "output artifacts must have unique names"
