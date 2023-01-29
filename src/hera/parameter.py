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
        return Parameter(name=self.name, description=self.description, default=self.default)

    def as_argument(self) -> Optional["Parameter"]:
        """Assembles the parameter for use as an argument of a task"""
        if self.value is None and self.value_from is None and self.default:
            # Argument not necessary as default is set for the input
            return None

        return Parameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            value=self.value,
            value_from=self.value_from,
        )

    def as_output(self) -> "Parameter":
        """Assembles the parameter for use as an output of a task"""
        return Parameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            enum=self.enum,
            value_from=self.value_from,
        )


__all__ = ["Parameter"]
