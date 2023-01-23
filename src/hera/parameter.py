"""Holds input model specifications"""
import json
from typing import Any, Optional

from pydantic import root_validator

from hera.models import Parameter as _ModelParameter


class Parameter(_ModelParameter):
    value: Optional[Any]

    @root_validator(pre=True)
    def _check_values(cls, values):
        if values.get("value") is not None and values.get("value_from") is not None:
            raise ValueError("Cannot specify both `value` and `value_from` when instantiating `Parameter`")

        if values.get("value") is not None and not isinstance(values.get("value"), str):
            values["value"] = json.dumps(values.get("value"))

        if values.get("default") is not None and not isinstance(values.get("value"), str):
            values["default"] = json.dumps(values.get("default"))

        return values

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

    def as_input(self) -> "Parameter":
        parameter = Parameter(name=self.name)
        if self.default is not None:
            parameter.default = self.default
        if self.description is not None:
            parameter.description = self.description
        return parameter


__all__ = ["Parameter"]
