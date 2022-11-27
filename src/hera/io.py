from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

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
    inputs: Union[
        List[Union[Parameter, Artifact]],
        List[Union[Parameter, Artifact, Dict[str, Any]]],
        Dict[str, Any],
    ] = None,
        `Input` or `Parameter` objects that hold parameter inputs. When a dictionary is specified all the key/value
        pairs will be transformed into `Parameter`s. The `key` will be the `name` field of the `Parameter` while the
        `value` will be the `value` field of the `Parameter.
    outputs: List[Union[Parameter, Artifact]]
        List of parameters or artifacts to use as outputs.
    """

    inputs: Union[
        List[Union[Parameter, Artifact]],
        List[Union[Parameter, Artifact, Dict[str, Any]]],
        Dict[str, Any],
    ] = field(  # type: ignore
        default_factory=lambda: []
    )
    outputs: List[Union[Parameter, Artifact]] = field(default_factory=lambda: [])

    def __post_init__(self) -> None:
        self.inputs = self._parse_inputs(self.inputs)

    def _parse_inputs(
        self,
        inputs: Union[
            List[Union[Parameter, Artifact]], List[Union[Parameter, Artifact, Dict[str, Any]]], Dict[str, Any]
        ],
    ) -> List[Union[Parameter, Artifact]]:
        """Parses the dictionary aspect of the specified inputs and returns a list of parameters and artifacts.

        Parameters
        ----------
        inputs: Union[Dict[str, Any], List[Union[Parameter, Artifact, Dict[str, Any]]]]
            The list of inputs specified on the task. The `Dict` aspect is treated as a mapped collection of
            Parameters. If a single dictionary is specified, all the fields are transformed into `Parameter`s. The key
            is the `name` of the `Parameter` and the `value` is the `value` field of the `Parameter.

        Returns
        -------
        List[Union[Parameter, Artifact]]
            A list of parameters and artifacts. The parameters contain the specified dictionary mapping as well, as
            independent parameters.
        """
        result: List[Union[Parameter, Artifact]] = []
        if isinstance(inputs, dict):
            for k, v in inputs.items():
                result.append(Parameter(k, value=v))
        else:
            for i in inputs:
                if isinstance(i, Parameter) or isinstance(i, Artifact):
                    result.append(i)
                elif isinstance(i, dict):
                    for k, v in i.items():
                        result.append(Parameter(k, value=v))
        return result

    def _build_inputs(self) -> Optional[IoArgoprojWorkflowV1alpha1Inputs]:
        """Assembles the inputs of the task."""
        parsed_inputs = self._parse_inputs(self.inputs)
        parameters = [obj.as_input() for obj in parsed_inputs if isinstance(obj, Parameter)]
        artifacts = [obj.as_input() for obj in parsed_inputs if isinstance(obj, Artifact)]
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
        i_parameters = [obj.as_input() for obj in self.inputs if isinstance(obj, Parameter)]
        i_artifacts = [obj.as_input() for obj in self.inputs if isinstance(obj, Artifact)]
        o_parameters = [obj.as_output() for obj in self.outputs if isinstance(obj, Parameter)]
        o_artifacts = [obj.as_output() for obj in self.outputs if isinstance(obj, Artifact)]
        assert len(set([i.name for i in i_parameters])) == len(i_parameters), "input parameters must have unique names"
        assert len(set([i.name for i in i_artifacts])) == len(i_artifacts), "input artifacts must have unique names"
        assert len(set([o.name for o in o_parameters])) == len(
            o_parameters
        ), "output parameters must have unique names"
        assert len(set([o.name for o in o_artifacts])) == len(o_artifacts), "output artifacts must have unique names"
