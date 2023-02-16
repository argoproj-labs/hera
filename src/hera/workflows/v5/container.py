from typing import List, Optional, Union

from hera.workflows.models import Artifact, Lifecycle
from hera.workflows.models import Parameter as ModelParameter
from hera.workflows.models import SecurityContext
from hera.workflows.v5._mixins import (
    _ContainerMixin,
    _EnvMixin,
    _IOMixin,
    _ResourceMixin,
    _TemplateMixin,
    _VolumeMountMixin,
)
from hera.workflows.v5.parameter import Parameter

Inputs = List[Union[Artifact, Parameter, ModelParameter]]
Outputs = List[Union[Artifact, Parameter, ModelParameter]]


class Container(_IOMixin, _ContainerMixin, _EnvMixin, _TemplateMixin, _ResourceMixin, _VolumeMountMixin):
    args: Optional[List[str]] = None
    command: Optional[List[str]] = None
    lifecycle: Optional[Lifecycle] = None
    name: Optional[str] = None
    security_context: Optional[SecurityContext] = None
    working_dir: Optional[str] = None
