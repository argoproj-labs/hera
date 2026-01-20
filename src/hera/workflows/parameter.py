"""The `hera.workflows.parameter` module provides the Parameter class.

Tip:
    [Read the Hera walk-through for Parameters.](../../../walk-through/parameters.md)
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, cast

from hera.shared.serialization import MISSING, serialize
from hera.workflows.models import Parameter as _ModelParameter
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ValueFrom


@dataclass(kw_only=True)
class Parameter:
    """A `Parameter` is used to pass values in and out of templates.

    They are to declare input and output parameters in the case of templates, and are used
    for Steps and Tasks to assign values.
    """

    # fields matching ModelParameter
    name: Optional[str] = None
    """the name of the Parameter in the template"""

    description: Optional[str] = None
    enum: Optional[List[str]] = None
    global_name: Optional[str] = None
    value_from: Optional[ValueFrom] = None

    # Special Hera fields
    output: Optional[bool] = False
    """used to specify parameter as an output in function signature annotations"""

    dumps: Optional[Callable[[Any], str]] = None
    """used to specify a dumper function to serialise an output parameter value as a string for Annotated parameters"""

    loads: Optional[Callable[[str], Any]] = None
    """used to specify a loader function to deserialise a string representation of an object for Annotated parameters"""

    def _check_name(self):
        if not self.name:
            raise ValueError("name cannot be `None` or empty when used")

    # `MISSING` is the default value so that `Parameter` serialization understands the difference between a
    # missing value and a value of `None`, as set by a user. With this, when something sets a value of `None` it is
    # taken as a proper `None`. By comparison, if a user does not set a value, it is taken as `MISSING` and therefore
    # not serialized. This happens because the values if turned into an _actual_ `None` by `serialize` and therefore
    # Pydantic will not include it in the YAML that is passed to Argo
    value: Optional[Any] = MISSING
    default: Optional[Any] = MISSING

    def __post_init__(self):
        """Perform post init validation and serialise values."""
        if self.value != MISSING and self.value_from is not None:
            raise ValueError("Cannot specify both `value` and `value_from` when instantiating `Parameter`")

        self.value = serialize(self.value)
        self.default = serialize(self.default)
        if self.enum:
            # We don't need to set "enum" in values to "MISSING" if there are no values
            # as it's a list of values. The values themselves should be serialized (and can be
            # assumed to be str).
            self.enum = [cast(str, serialize(v)) for v in self.enum]

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input parameter annotations."""
        return ["enum", "description", "default", "name", "value", "value_from"]

    def __str__(self):
        """Represent the parameter as a string by pointing to its value.

        This is useful in situations where we want to concatenate string values such as
        Task.args=["echo", wf.get_parameter("message")].
        """
        if self.value is None:
            raise ValueError("Cannot represent `Parameter` as string as `value` is not set")
        return self.value

    @classmethod
    def from_model(cls, model: _ModelParameter) -> Parameter:
        """Creates a `Parameter` from a `Parameter` model without running validation."""
        return cls(**model.dict())

    def with_name(self, name: str) -> Parameter:
        """Returns a copy of the parameter with the name set to the value."""
        p = deepcopy(self)
        p.name = name
        return p

    def as_input(self) -> _ModelParameter:
        """Assembles the parameter for use as an input of a template."""
        self._check_name()
        assert self.name
        return _ModelParameter(
            name=self.name,
            description=self.description,
            default=self.default,
            enum=self.enum,
            value=self.value,
            value_from=self.value_from,
        )

    def as_argument(self) -> _ModelParameter:
        """Assembles the parameter for use as an argument of a step or a task."""
        # Setting a default value when used as an argument is a no-op so we exclude it as it would get overwritten by
        # `value` or `value_from` (one of which is required)
        # Overwrite ref: https://github.com/argoproj/argo-workflows/blob/781675ddcf6f1138d697cb9c71dae484daa0548b/workflow/common/util.go#L126-L139
        # One of value/value_from required ref: https://github.com/argoproj/argo-workflows/blob/ab178bb0b36a5ce34b4c1302cf4855879a0e8cf5/workflow/validate/validate.go#L794-L798
        self._check_name()
        assert self.name
        return _ModelParameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            enum=self.enum,
            value=self.value,
            value_from=self.value_from,
        )

    def as_output(self) -> _ModelParameter:
        """Assembles the parameter for use as an output of a template."""
        # Only `value` and `value_from` are valid here
        # see https://github.com/argoproj/argo-workflows/blob/e3254eca115c9dd358e55d16c6a3d41403c29cae/workflow/validate/validate.go#L1067
        self._check_name()
        assert self.name
        return _ModelParameter(
            name=self.name,
            global_name=self.global_name,
            description=self.description,
            value=self.value,
            value_from=self.value_from,
        )


__all__ = ["Parameter"]
