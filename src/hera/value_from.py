from dataclasses import dataclass
from typing import Optional

from argo_workflows.models import (
    ConfigMapKeySelector,
    IoArgoprojWorkflowV1alpha1ValueFrom,
)


@dataclass
class ValueFrom:
    """Holds descriptions of where to obtain parameter values from.

    Attributes
    ----------
    config_map_key_ref: Optional[str] = None
        A selector that identifies a config map to obtain the value from.
    default: Optional[str] = None
        Specifies a value to be used if retrieving the value from the specified source fails.
    event: Optional[str] = None
        Selector that is evaluated against the event to get the value of the parameter e.g. 'payload.message'. See
        https://github.com/antonmedv/expr for more examples and full documentation as it is the package used by Argo.
    expression: Optional[str] = None
        A specification of the value of the parameter.
    jq_filter: Optional[str] = None
        JQFilter expression against the resource object in resource templates to obtain a value from.
    json_path: Optional[str] = None
        The JSON path of a resource to retrieve an output parameter value from in resource templates.
    parameter: Optional[str] = None
        Parameter reference to a task or DAG in which to retrieve an output parameter value from,
        e.g. '{{tasks.t.outputs.param}}'). Note that you can obtain such specification via `task.get_parameter(...)`,
        `dag.get_parameter(...)`, and `workflow.get_parameter(...)`.
    path: Optional[str] = None
        Path in the container to retrieve an output parameter value from in container templates.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/fields/#valuefrom
    """

    config_map_key_ref: Optional[str] = None
    default: Optional[str] = None
    event: Optional[str] = None
    expression: Optional[str] = None
    jq_filter: Optional[str] = None
    json_path: Optional[str] = None
    parameter: Optional[str] = None
    path: Optional[str] = None

    def __post_init__(self):
        fields = vars(self)
        if all([v is None for v in fields.values()]):
            raise ValueError("At least one fields must be not `None` for `ValueFrom`")

    def build(self) -> IoArgoprojWorkflowV1alpha1ValueFrom:
        value_from = IoArgoprojWorkflowV1alpha1ValueFrom()
        if self.config_map_key_ref is not None:
            setattr(value_from, "config_map_key_ref", ConfigMapKeySelector(self.config_map_key_ref))
        if self.default is not None:
            setattr(value_from, "default", self.default)
        if self.event is not None:
            setattr(value_from, "event", self.event)
        if self.expression is not None:
            setattr(value_from, "expression", self.expression)
        if self.jq_filter is not None:
            setattr(value_from, "jq_filter", self.jq_filter)
        if self.json_path is not None:
            setattr(value_from, "json_path", self.json_path)
        if self.parameter is not None:
            setattr(value_from, "parameter", self.parameter)
        if self.path is not None:
            setattr(value_from, "path", self.path)
        return value_from
