"""Holds input model specifications"""
import json
from typing import Any, List, Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Parameter,
    IoArgoprojWorkflowV1alpha1ValueFrom,
)

from hera.value_from import ValueFrom


class Parameter:
    """A representation of input from one task to another.

    Parameters
    ----------
    name: str
        The name of the task to take input from. The task's results are expected via stdout. Specifically, the task is
        expected to perform the script illustrated in Examples.
    value: Optional[Any] = None
        Value of the parameter, as an index into some field of the task. If this is left as `None`, along with
        `value_from` being left as `None`, as is the case in GitOps patterns, the submitter has to likely supply the
        parameter value via the Argo CLI. Note that if a value is supplied a `json.dumps` will be applied to it.
    default: Optional[str] = None
        Default value of the parameter in case the `value` cannot be obtained based on the specification.
    value_from: Optional[ValueFrom] = None
        Describes a location in which to obtain the value to a parameter. See `hera.value_from.ValueFrom` or
        https://argoproj.github.io/argo-workflows/fields/#valuefrom.
    description: Optional[str] = None
        An optional parameter description.
    enum: Optional[List[str]] = None
        Holds a list of string values to choose from, for the actual value of the parameter.
    global_name: Optional[str] = None
        Exports an output parameter to the global scope, making it available as
        '{{workflow.outputs.parameters.XXXX}} and in workflow.status.outputs.parameters.
    """

    def __init__(
        self,
        name: str,
        value: Optional[Any] = None,
        default: Optional[str] = None,
        value_from: Optional[ValueFrom] = None,
        description: Optional[str] = None,
        enum: Optional[List[str]] = None,
        global_name: Optional[str] = None,
    ) -> None:
        if value is not None and value_from is not None:
            raise ValueError("Cannot specify both `value` and `value_from` when instantiating `Parameter`")
        self.name = name
        if value is None or isinstance(value, str):
            self.value = value
        else:
            self.value = json.dumps(value)  # None serialized as `null`
        self.default = str(default) if default is not None else None
        self.value_from = value_from
        self.description = description
        self.enum = enum
        self.global_name = global_name

    def as_name(self, name: str) -> "Parameter":
        """Changes the name of the parameter."""
        self.name = name
        return self

    def as_argument(self) -> Optional[IoArgoprojWorkflowV1alpha1Parameter]:
        """Assembles the parameter for use as an argument of a task"""
        if self.value is None and self.value_from is None and self.default:
            # Argument not necessary as default is set for the input.
            return None
        parameter = IoArgoprojWorkflowV1alpha1Parameter(name=self.name)
        if self.global_name is not None:
            setattr(parameter, "global_name", self.global_name)
        if self.description is not None:
            setattr(parameter, "description", self.description)

        if self.value is not None:
            setattr(parameter, "value", self.value)
        elif self.value_from is not None:
            setattr(parameter, "value_from", self.value_from.build())
        return parameter

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        """Assembles the parameter for use as an input to task"""
        parameter = IoArgoprojWorkflowV1alpha1Parameter(name=self.name)
        if self.default:
            setattr(parameter, "default", self.default)
        if self.description is not None:
            setattr(parameter, "description", self.description)
        return parameter

    def as_output(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        """Assembles the parameter for use as an output of a task"""
        parameter = IoArgoprojWorkflowV1alpha1Parameter(name=self.name)
        if self.value_from:
            setattr(parameter, "value_from", self.value_from.build())
        else:
            argo_value_from = IoArgoprojWorkflowV1alpha1ValueFrom(parameter=self.value)
            if self.default:
                setattr(argo_value_from, "default", self.default)
            setattr(parameter, "value_from", argo_value_from)

        if self.global_name is not None:
            setattr(parameter, "global_name", self.global_name)
        if self.description is not None:
            setattr(parameter, "description", self.description)
        if self.enum is not None:
            setattr(parameter, "enum", self.enum)
        return parameter

    def __str__(self):
        """Represent the parameter as a string by pointing to its value.

        This is useful in situations where we want to concatenate string values such as
        Task.args=["echo", wf.get_parameter("message")].
        """
        if self.value is None:
            raise ValueError("Cannot represent `Parameter` as string as `value` is not set")
        return self.value

    @property
    def contains_item(self) -> bool:
        """Check whether the parameter contains an argo item reference"""
        if self.value is None:
            return False
        elif "{{item" in self.value:
            return True
        return False
