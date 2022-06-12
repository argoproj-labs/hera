"""Holds input model specifications"""
from typing import List, Union

from argo_workflows.models import IoArgoprojWorkflowV1alpha1Parameter


class Input:
    """A representation of input from one task to another.

    Parameters
    ----------
    name: str
        The name of the task to take input from. The task's results are expected via stdout. Specifically, the task is
        expected to perform the script illustrated in Examples.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def get_spec(self) -> Union[IoArgoprojWorkflowV1alpha1Parameter, List[IoArgoprojWorkflowV1alpha1Parameter]]:
        raise NotImplementedError('Implement')


class InputParameter(Input):
    """A representation of an input from another task.

    Parameters
    ----------
    name: str
        The name of the task to take input from. The task's results are expected via stdout. Specifically, the task is
        expected to perform the script illustrated in Examples.
    from_task: str
        Name of the task whose output parameter this input represents.
    parameter_name: str
        The name of the parameter from the other task to encode as input to a task.
    """

    from_task: str
    parameter_name: str

    def __init__(self, name: str, from_task: str, parameter_name: str) -> None:
        super().__init__(name)
        self.from_task = from_task
        self.parameter_name = parameter_name

    def get_spec(self) -> Union[IoArgoprojWorkflowV1alpha1Parameter, List[IoArgoprojWorkflowV1alpha1Parameter]]:
        from_ = f"{{{{tasks.{self.from_task}.outputs.parameters.{self.parameter_name}}}}}"
        return IoArgoprojWorkflowV1alpha1Parameter(
            name=self.name,
            value=from_,
        )


class InputFrom(Input):
    """A representation of input from one task to another in the form of STDOUT.

    This is typically used on a task definition to represent the task another task is supposed to take input from and
    what parameters ought to be set by the output.

    Parameters
    ----------
    name: str
        The name of the task to take input from. The task's results are expected via stdout.
    parameters: List[str]
        The list of parameter names to provide as input to the existing task.
    """

    parameters: List[str]

    def __init__(self, name: str, parameters: List[str]) -> None:
        super().__init__(name)
        self.parameters = parameters

    def get_spec(self) -> Union[IoArgoprojWorkflowV1alpha1Parameter, List[IoArgoprojWorkflowV1alpha1Parameter]]:
        result = []
        for parameter in self.parameters:
            result.append(IoArgoprojWorkflowV1alpha1Parameter(name=parameter, value=f'{{{{item.{parameter}}}}}'))
        return result
