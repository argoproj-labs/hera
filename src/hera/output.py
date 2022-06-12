"""Holds output model specifications"""
from typing import Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Parameter,
    IoArgoprojWorkflowV1alpha1ValueFrom,
)


class Output:
    """Output represents the default output of a task.

    Independent output types are implemented by subclasses of `Output`.

    Parameters
    ----------
    name: str
        Name of the output.
    default: Optional[str] = None
        The optional default value of the parameter.
    """

    def __init__(
        self,
        name: str,
        default: Optional[str] = None,
    ) -> None:
        self.name = name
        self.default = default

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        return IoArgoprojWorkflowV1alpha1Parameter(
            name=self.name,
            default=self.default,
        )


class OutputPathParameter(Output):
    """Output path represents a parameter that encodes the content of a file located at a given path.

    Parameters
    ----------
    name: str
        Name of the output.
    path: str
        Path to the file containing the output.
    default: Optional[str] = None
        The optional default value of the parameter.
    """

    def __init__(self, name: str, path: str, default: Optional[str] = None) -> None:
        super().__init__(name, default=default)
        self.path = path

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Parameter:
        if self.default is not None:
            return IoArgoprojWorkflowV1alpha1Parameter(
                name=self.name,
                value_from=IoArgoprojWorkflowV1alpha1ValueFrom(
                    default=self.default,
                    path=self.path,
                ),
            )
        return IoArgoprojWorkflowV1alpha1Parameter(
            name=self.name,
            value_from=IoArgoprojWorkflowV1alpha1ValueFrom(
                path=self.path,
            ),
        )
