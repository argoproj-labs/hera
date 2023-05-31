"""The parameter module provides the Parameter class.

See https://argoproj.github.io/argo-workflows/walk-through/parameters/
for a tutorial on Parameters.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import root_validator

from hera.shared.serialization import MISSING, serialize
from hera.workflows.models import Parameter as _ModelParameter


class Parameter(_ModelParameter):
    """A `Parameter` is used to pass values in and out of templates.

    They are to declare input and output parameters in the case of templates, and are used
    for Steps and Tasks to assign values.
    """

    # `MISSING` is the default value so that `Parameter` serialization understands the difference between a
    # missing value and a value of `None`, as set by a user. With this, when something sets a value of `None` it is
    # taken as a proper `None`. By comparison, if a user does not set a value, it is taken as `MISSING` and therefore
    # not serialized. This happens because the values if turned into an _actual_ `None` by `serialize` and therefore
    # Pydantic will not include it in the YAML that is passed to Argo
    value: Optional[Any] = MISSING
    default: Optional[Any] = MISSING

    @root_validator(pre=True, allow_reuse=True)
    def _check_values(cls, values):
        if values.get("value") is not None and values.get("value_from") is not None:
            raise ValueError("Cannot specify both `value` and `value_from` when instantiating `Parameter`")

        values["value"] = serialize(values.get("value", MISSING))
        values["default"] = serialize(values.get("default", MISSING))

        return values

    def __str__(self):
        """Represent the parameter as a string by pointing to its value.

        This is useful in situations where we want to concatenate string values such as
        Task.args=["echo", wf.get_parameter("message")].
        """
        if self.value is None:
            raise ValueError("Cannot represent `Parameter` as string as `value` is not set")
        return self.value

    def with_name(self, name: str) -> Parameter:
        """Returns a copy of the parameter with the name set to the value"""
        p = self.copy(deep=True)
        p.name = name
        return p

    def as_input(self) -> _ModelParameter:
        """Assembles the parameter for use as an input of a template"""
        return _ModelParameter(
            name=self.name,
            description=self.description,
            default=self.default,
            enum=self.enum,
            value=self.value,
            value_from=self.value_from,
        )

    def as_argument(self) -> _ModelParameter:
        """Assembles the parameter for use as an argument of a step or a task"""
        # Setting a default value when used as an argument is a no-op so we exclude it as it would get overwritten by
        # `value` or `value_from` (one of which is required)
        # Overwrite ref: https://github.com/argoproj/argo-workflows/blob/781675ddcf6f1138d697cb9c71dae484daa0548b/workflow/common/util.go#L126-L139
        # One of value/value_from required ref: https://github.com/argoproj/argo-workflows/blob/ab178bb0b36a5ce34b4c1302cf4855879a0e8cf5/workflow/validate/validate.go#L794-L798
        return _ModelParameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            enum=self.enum,
            value=self.value,
            value_from=self.value_from,
        )

    def as_output(self) -> _ModelParameter:
        """Assembles the parameter for use as an output of a template"""
        # Only `value` and `value_from` are valid here
        # see https://github.com/argoproj/argo-workflows/blob/e3254eca115c9dd358e55d16c6a3d41403c29cae/workflow/validate/validate.go#L1067
        return _ModelParameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            value=self.value,
            value_from=self.value_from,
        )


__all__ = ["Parameter"]
