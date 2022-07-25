"""Holds input model specifications"""
from typing import Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Parameter,
    IoArgoprojWorkflowV1alpha1ValueFrom,
)

# Alias
ValueFrom = IoArgoprojWorkflowV1alpha1ValueFrom


class Parameter:
    """A representation of input from one task to another.

    Parameters
    ----------
    name: str
        The name of the task to take input from. The task's results are expected via stdout. Specifically, the task is
        expected to perform the script illustrated in Examples.
    """

    def __init__(
        self,
        name: str,
        value: Optional[str] = None,
        default: Optional[str] = None,
        value_from: Optional[ValueFrom] = None,
    ) -> None:
        if value is not None and value_from is not None:
            raise ValueError("`value` and `value_from` args must be exclusive")
        self.name = name
        self.value = value
        self.default = default
        self.value_from = value_from

    def as_argument(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        parameter = IoArgoprojWorkflowV1alpha1Parameter(
            name=self.name,
        )
        if self.default:
            setattr(parameter, "default", self.default)
        if self.value is not None:
            setattr(parameter, "value", self.value)
        elif self.value_from is not None:
            setattr(parameter, "value_from", self.value_from)
        return parameter

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        return IoArgoprojWorkflowV1alpha1Parameter(name=self.name)

    def as_output(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        return IoArgoprojWorkflowV1alpha1Parameter(name=self.name, value_from=self.value_from)


# class GlobalInputParameter(Input):
#     """A representation of a global workflow input.

#     Parameters
#     ----------
#     name: str
#         The name of the parameter.
#     parameter_name: str
#         The name of the global parameter to expose to the task.
#     """

#     def __init__(self, name: str, parameter_name: str) -> None:
#         super().__init__(name)
#         self.parameter_name = parameter_name

#     def get_spec(self) -> Union[IoArgoprojWorkflowV1alpha1Parameter, List[IoArgoprojWorkflowV1alpha1Parameter]]:
#         return IoArgoprojWorkflowV1alpha1Parameter(
#             name=self.name, value=f"{{{{workflow.parameters.{self.parameter_name}}}}}"
#         )


# class MultiInput(Input):
#     """A representation of an input from another task's aggregated output.

#     Parameters
#     ----------
#     name: str
#         The name of the parameter.
#     from_task: str
#         Name of the task whose output parameter this input represents.

#     Notes
#     -----
#     Fan-in: Combining the outputs
#     When reading the elements, Argo reads the output of the previous step from "output-number" as JSON objects fo
#     all output parameters. The input to this step will then be a JSON-compliant array of objects like so:
#         [{"number":"1"},{"number":"2"},{"number":"3"}]

#     The ints were converted into strings since Argo considers all inputs and outputs to be strings by default.
#     """

#     def __init__(self, name: str, from_task: str) -> None:
#         super().__init__(name)
#         self.from_task = from_task

#     def get_spec(self) -> Union[IoArgoprojWorkflowV1alpha1Parameter, List[IoArgoprojWorkflowV1alpha1Parameter]]:
#         return IoArgoprojWorkflowV1alpha1Parameter(
#             name=self.name, value=f"{{{{tasks.{self.from_task}.outputs.parameters}}}}"
#         )
