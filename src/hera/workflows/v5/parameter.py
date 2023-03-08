"""Holds input model specifications"""
import json
from typing import Any, Optional

from pydantic import root_validator

from hera.workflows.models import Parameter as _ModelParameter

MISSING = object()


def _serialize(value: Any):
    if value is MISSING:
        return None
    elif isinstance(value, str):
        return value
    else:
        return json.dumps(value)  # None serialized as `null`


class Parameter(_ModelParameter):
    value: Optional[Any]

    @root_validator(pre=True)
    def _check_values(cls, values):
        if values.get("value") is not None and values.get("value_from") is not None:
            raise ValueError("Cannot specify both `value` and `value_from` when instantiating `Parameter`")

        if values.get("value") is not None and not isinstance(values.get("value"), str):
            values["value"] = _serialize(values.get("value"))

        if values.get("default") is not None and not isinstance(values.get("value"), str):
            values["default"] = _serialize(values.get("default"))

        return values

    def __str__(self):
        """Represent the parameter as a string by pointing to its value.

        This is useful in situations where we want to concatenate string values such as
        Task.args=["echo", wf.get_parameter("message")].
        """
        if self.value is None:
            raise ValueError("Cannot represent `Parameter` as string as `value` is not set")
        return self.value

    def as_input(self) -> _ModelParameter:
        return _ModelParameter(
            name=self.name,
            description=self.description,
            default=self.default,
            enum=self.enum,
            value=self.value,
            value_from=self.value_from,
        )

    def as_argument(self) -> Optional[_ModelParameter]:
        """Assembles the parameter for use as an argument of a task"""
        return _ModelParameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            value=self.value,
            value_from=self.value_from,
            enum=self.enum,
        )

    def as_output(self) -> _ModelParameter:
        """Assembles the parameter for use as an output of a task"""
        # Only value and value_from are valid here
        # see https://github.com/argoproj/argo-workflows/blob/e3254eca115c9dd358e55d16c6a3d41403c29cae/workflow/validate/validate.go#L1067
        return _ModelParameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            value_from=self.value_from,
            value=self.value,
        )


__all__ = ["Parameter"]
