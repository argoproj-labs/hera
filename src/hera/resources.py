"""Holds the resource specification"""
from dataclasses import dataclass
from typing import Dict, Optional, Union

from argo_workflows.models import ResourceRequirements

from hera.validators import validate_storage_units


# TODO: Move function?
def merge_dicts(a: Dict, b: Dict, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


@dataclass
class Resources:
    """A representation of a collection of resources that are requested to be consumed by a task for execution.

    gpus: Optional[int]
        The number of GPUs to request as part of the workflow.
    """

    cpu_request: Optional[Union[int, str]] = None
    cpu_limit: Optional[Union[int, str]] = None
    memory_request: Optional[str] = None
    memory_limit: Optional[str] = None
    gpus: Optional[int] = None
    custom_resources: Optional[Dict] = None

    def __post_init__(self):
        if self.memory_request:
            validate_storage_units(self.memory_request)
        if self.memory_limit:
            validate_storage_units(self.memory_limit)
        # TODO: add validation for CPU units if str

        if self.cpu_limit is not None and isinstance(self.cpu_limit, int):
            assert self.cpu_limit >= 0, "CPU limit must be positive"
        if self.cpu_request is not None and isinstance(self.cpu_request, int):
            assert self.cpu_request >= 0, "CPU request must be positive"
            if self.cpu_limit is not None and isinstance(self.cpu_limit, int):
                assert self.cpu_request <= self.cpu_limit, "CPU request must be smaller or equal to limit"

    def build(self) -> ResourceRequirements:
        resources = dict()

        if self.cpu_limit:
            resources = merge_dicts(resources, dict(limit=dict(cpu=self.cpu_limit)))

        if self.cpu_request:
            resources = merge_dicts(resources, dict(request=dict(cpu=self.cpu_request)))

        if self.memory_limit:
            resources = merge_dicts(resources, dict(limit=dict(memory=self.memory_limit)))

        if self.memory_request:
            resources = merge_dicts(resources, dict(request=dict(memory=self.memory_request)))

        if self.gpus:
            resources = merge_dicts(resources, dict(request={"nvidia.com/gpu": self.gpus}))
            resources = merge_dicts(resources, dict(limit={"nvidia.com/gpu": self.gpus}))

        if self.custom_resources:
            resources = merge_dicts(resources, self.custom_resources)

        return ResourceRequirements(**resources)
