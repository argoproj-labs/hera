from dataclasses import dataclass
from typing import List, Optional, Union

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Outputs,
)

from hera.artifact import Artifact
from hera.parameter import Parameter


@dataclass
class IO:
    """Input/output high-level representation.

    Parameters
    ----------
    inputs: List[Union[Parameter, Artifact]]
        List of parameters or artifacts to use as inputs.
    outputs: List[Union[Parameter, Artifact]]
        List of parameters or artifacts to use as outputs.
    """

    inputs: List[Union[Parameter, Artifact]]
    outputs: List[Union[Parameter, Artifact]]

    def _build_inputs(self) -> Optional[IoArgoprojWorkflowV1alpha1Inputs]:
        """Assembles the inputs of the task."""
        parameters = [obj.as_input() for obj in self.inputs if isinstance(obj, Parameter)]
        artifacts = [obj.as_input() for obj in self.inputs if isinstance(obj, Artifact)]
        if len(parameters) + len(artifacts) == 0:
            return None
        inputs = IoArgoprojWorkflowV1alpha1Inputs()
        if parameters:
            setattr(inputs, "parameters", parameters)
        if artifacts:
            setattr(inputs, "artifacts", artifacts)
        return inputs

    def _build_outputs(self) -> Optional[IoArgoprojWorkflowV1alpha1Outputs]:
        """Assembles and returns the task outputs"""
        parameters = [obj.as_output() for obj in self.outputs if isinstance(obj, Parameter)]
        artifacts = [obj.as_output() for obj in self.outputs if isinstance(obj, Artifact)]
        if len(parameters) + len(artifacts) == 0:
            return None
        outputs = IoArgoprojWorkflowV1alpha1Outputs()
        if parameters:
            setattr(outputs, "parameters", parameters)
        if artifacts:
            setattr(outputs, "artifacts", artifacts)
        return outputs

    def _validate_io(self):
        """
        Validates that the given function and corresponding params fit one another, raises AssertionError if
        conditions are not satisfied.
        """
        assert len(set([i.name for i in self.inputs])) == len(self.inputs), "input objects must have unique names"
        assert len(set([o.name for o in self.outputs])) == len(self.outputs), "output objects must have unique names"
