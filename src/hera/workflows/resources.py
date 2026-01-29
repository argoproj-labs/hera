"""The `hera.workflows.resources` module provides the Resources class for setting CPU, memory and other limits."""

from dataclasses import dataclass
from typing import Dict, Optional, Union

from hera.workflows.converters import convert_cpu_units, convert_memory_units, convert_storage_units
from hera.workflows.models import ResourceRequirements as _ModelResourceRequirements
from hera.workflows.validators import validate_cpu_units, validate_memory_units, validate_storage_units


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


@dataclass(kw_only=True)
class Resources:
    """A representation of a collection of resources that are requested to be consumed by a task for execution.

    This follow the K8S definition for resources.

    Attributes:
        cpu_request: The number of CPUs to request, either as a fraction (millicpu), whole number, or a string.
        cpu_limit: The limit of CPUs to request, either as a fraction (millicpu), whole number, or a string.
        memory_request: The amount of memory to request.
        memory_limit: The memory limit of the pod.
        ephemeral_request: The amount of ephemeral storage to request.
        ephemeral_limit: The ephemeral storage limit of the pod.
        gpus: The number of GPUs to request.
        gpu_flag: The GPU flag to use for identifying how many GPUs to mount to a pod. This is dependent on the cloud provider.
        custom_resources: Any custom resources to request. This is dependent on the cloud provider.

    Notes:
        Most of the fields that support a union of `int` and `str` support either specifying a number for the resource,
        such as 1 CPU, 2 GPU, etc., a `str` representation of that numerical resource, such as '1' CPU, '2' GPU, etc., but
        also supports specifying a *to be computed* value, such as `{{inputs.parameters.cpu_request}}`. This means tasks,
        steps, etc., can be stitched together in a way to have a task/step that *computes* the resource requirements, and
        then `outputs` them to the next step/task.
    """

    cpu_request: Optional[Union[float, int, str]] = None
    cpu_limit: Optional[Union[float, int, str]] = None
    memory_request: Optional[str] = None
    memory_limit: Optional[str] = None
    ephemeral_request: Optional[str] = None
    ephemeral_limit: Optional[str] = None
    gpus: Optional[Union[int, str]] = None
    gpu_flag: Optional[str] = "nvidia.com/gpu"
    custom_resources: Optional[Dict] = None

    def __post_init__(self):
        """Perform validation of values."""
        if self.memory_request is not None:
            validate_memory_units(self.memory_request)
        if self.memory_limit is not None:
            validate_memory_units(self.memory_limit)
            if self.memory_request is not None:
                if convert_memory_units(self.memory_request) > convert_memory_units(self.memory_limit):
                    raise ValueError("Memory request must be smaller or equal to limit")

        if self.ephemeral_request is not None:
            validate_storage_units(self.ephemeral_request)
        if self.ephemeral_limit is not None:
            validate_storage_units(self.ephemeral_limit)
            if self.ephemeral_request is not None:
                if convert_storage_units(self.ephemeral_request) > convert_storage_units(self.ephemeral_limit):
                    raise ValueError("Ephemeral request must be smaller or equal to limit")

        if self.cpu_request is not None and isinstance(self.cpu_request, (int, float)):
            if self.cpu_request < 0:
                raise ValueError("CPU request must be positive")
        if self.cpu_limit is not None and isinstance(self.cpu_limit, (int, float)):
            if self.cpu_limit < 0:
                raise ValueError("CPU limit must be positive")
            if self.cpu_request is not None and isinstance(self.cpu_request, (int, float)):
                if self.cpu_request > self.cpu_limit:
                    raise ValueError("CPU request must be smaller or equal to limit")

        if self.cpu_request is not None and isinstance(self.cpu_request, str):
            validate_cpu_units(self.cpu_request)
        if self.cpu_limit is not None and isinstance(self.cpu_limit, str):
            validate_cpu_units(self.cpu_limit)
            if self.cpu_request is not None and isinstance(self.cpu_request, str):
                if convert_cpu_units(self.cpu_request) > convert_cpu_units(self.cpu_limit):
                    raise ValueError("CPU request must be smaller or equal to limit")

    def build(self) -> _ModelResourceRequirements:
        """Builds the resource requirements of the pod."""
        resources: Dict = dict()

        if self.cpu_limit is not None:
            resources = _merge_dicts(resources, dict(limits=dict(cpu=str(self.cpu_limit))))

        if self.cpu_request is not None:
            resources = _merge_dicts(resources, dict(requests=dict(cpu=str(self.cpu_request))))

        if self.memory_limit is not None:
            resources = _merge_dicts(resources, dict(limits=dict(memory=self.memory_limit)))

        if self.memory_request is not None:
            resources = _merge_dicts(resources, dict(requests=dict(memory=self.memory_request)))

        if self.ephemeral_limit is not None:
            resources = _merge_dicts(resources, dict(limits={"ephemeral-storage": self.ephemeral_limit}))

        if self.ephemeral_request is not None:
            resources = _merge_dicts(resources, dict(requests={"ephemeral-storage": self.ephemeral_request}))

        if self.gpus is not None:
            resources = _merge_dicts(resources, dict(requests={self.gpu_flag: str(self.gpus)}))
            resources = _merge_dicts(resources, dict(limits={self.gpu_flag: str(self.gpus)}))

        if self.custom_resources:
            resources = _merge_dicts(resources, self.custom_resources)

        return _ModelResourceRequirements(**resources)


__all__ = ["Resources"]
