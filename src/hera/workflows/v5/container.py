from typing import List, Optional

from hera.workflows.models import Lifecycle
from hera.workflows.models import SecurityContext
from hera.workflows.v5._mixins import (
    _ContainerMixin,
    _DAGTaskMixin,
    _EnvMixin,
    _IOMixin,
    _ResourceMixin,
    _TemplateMixin,
    _VolumeMountMixin,
)
from hera.workflows.v5.buildable import Buildable


class Container(
    Buildable, _IOMixin, _DAGTaskMixin, _ContainerMixin, _EnvMixin, _TemplateMixin, _ResourceMixin, _VolumeMountMixin
):
    name: str
    args: Optional[List[str]] = None
    command: Optional[List[str]] = None
    lifecycle: Optional[Lifecycle] = None
    security_context: Optional[SecurityContext] = None
    working_dir: Optional[str] = None
