"""Holds the resource specification"""
from dataclasses import dataclass
from typing import Dict, Optional, Union

from argo_workflows.models import ResourceRequirements

from hera.validators import validate_storage_units


# TODO: Move function?
def _merge_dicts(a: Dict, b: Dict, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception("Conflict at `%s`" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


@dataclass
class Resources:
    """A representation of a collection of resources that are requested to be consumed by a task for execution.

    This follow the K8S definition for resources.

    Parameters
    ----------
    cpu_request: Optional[Union[float, int, str]] = None
        The number of CPUs to request, either as a fraction (millicpu), whole number, or a string.
    cpu_limit: Optional[Union[int, str]] = None
        The limit of CPUs to request, either as a fraction (millicpu), whole number, or a string.
    memory_request: Optional[str] = None
        The amount of memory to request.
    memory_limit: Optional[str] = None
        The memory limit of the pod.
    gpus: Optional[int] = None
        The number of GPUs to request.
    gpu_flag: Optional[str] = "nvidia.com/gpu"
        The GPU flag to use for identifying how many GPUs to mount to a pod. This is dependent on the cloud provider.
    custom_resources: Optional[Dict] = None
        Any custom resources to request. This is dependent on the cloud provider.
    """

    cpu_request: Optional[Union[float, int, str]] = None
    cpu_limit: Optional[Union[float, int, str]] = None
    memory_request: Optional[str] = None
    memory_limit: Optional[str] = None
    gpus: Optional[int] = None
    gpu_flag: Optional[str] = "nvidia.com/gpu"
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

        if self.cpu_request is None and self.cpu_limit is not None:
            self.cpu_request = self.cpu_limit
        if self.memory_request is None and self.memory_limit is not None:
            self.memory_request = self.memory_limit

    def build(self) -> ResourceRequirements:
        """Builds the resource requirements of the pod"""
        resources: Dict = dict()

        if self.cpu_limit is not None:
            resources = _merge_dicts(resources, dict(limits=dict(cpu=str(self.cpu_limit))))

        if self.cpu_request is not None:
            resources = _merge_dicts(resources, dict(requests=dict(cpu=str(self.cpu_request))))

        if self.memory_limit is not None:
            resources = _merge_dicts(resources, dict(limits=dict(memory=self.memory_limit)))

        if self.memory_request is not None:
            resources = _merge_dicts(resources, dict(requests=dict(memory=self.memory_request)))

        if self.gpus is not None:
            resources = _merge_dicts(resources, dict(requests={self.gpu_flag: str(self.gpus)}))
            resources = _merge_dicts(resources, dict(limits={self.gpu_flag: str(self.gpus)}))

        if self.custom_resources:
            resources = _merge_dicts(resources, self.custom_resources)

        return ResourceRequirements(**resources)
