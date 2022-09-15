"""Holds input model specifications"""
from typing import Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Parameter,
    IoArgoprojWorkflowV1alpha1ValueFrom,
)


class Parameter:
    """A representation of input from one task to another.

    Parameters
    ----------
    name: str
        The name of the task to take input from. The task's results are expected via stdout. Specifically, the task is
        expected to perform the script illustrated in Examples.
    value: Optional[str] = None
        Value of the parameter, as an index into some field of the task.
    default: Optional[str] = None
        Default value of the parameter in case the `value` cannot be obtained based on the specification.
    value_from: Optional[dict] = None
        Describes a location in which to obtain the value to a parameter.
        See https://argoproj.github.io/argo-workflows/fields/#valuefrom.
    """

    def __init__(
        self,
        name: str,
        value: Optional[str] = None,
        default: Optional[str] = None,
        value_from: Optional[dict] = None,
    ) -> None:
        if value is not None and value_from is not None:
            raise ValueError("`value` and `value_from` args must be exclusive")
        self.name = name
        self.value = value
        self.default = default
        self.value_from = value_from

    def as_argument(self) -> Optional[IoArgoprojWorkflowV1alpha1Parameter]:
        """Assembles the parameter for use as an argument of a task"""
        if self.value is None and self.value_from is None and self.default:
            # Argument not necessary as default is set for the input.
            return None
        parameter = IoArgoprojWorkflowV1alpha1Parameter(
            name=self.name,
        )
        if self.value:
            setattr(parameter, "value", self.value)
        elif self.value_from is not None:
            setattr(parameter, "value_from", IoArgoprojWorkflowV1alpha1ValueFrom(**self.value_from))
        else:
            raise ValueError(
                f"Parameter with name `{parameter.name}` cannot be interpreted as argument as neither of the following args are set: `value`, `value_from`, `default`"  # noqa
            )
        return parameter

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        """Assembles the parameter for use as an input to task"""
        parameter = IoArgoprojWorkflowV1alpha1Parameter(name=self.name)
        if self.default:
            setattr(parameter, "default", self.default)
        return parameter

    def as_output(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        """Assembles the parameter for use as an output of a task"""
        if self.value_from:
            return IoArgoprojWorkflowV1alpha1Parameter(
                name=self.name, value_from=IoArgoprojWorkflowV1alpha1ValueFrom(**self.value_from)
            )
        else:
            argo_value_from = IoArgoprojWorkflowV1alpha1ValueFrom(parameter=self.value)
            if self.default:
                setattr(argo_value_from, "default", self.default)
            return IoArgoprojWorkflowV1alpha1Parameter(name=self.name, value_from=argo_value_from)

    def __str__(self):
        """
        Represent the parameter as a string by pointing to its value.
        This is useful in situations where we want to concatinate string values, like
        Task.args=["echo", wf.get_parameter("message")]
        """
        if self.value:
            return self.value
        raise ValueError("Cannot represent as string as `value` is not set")
