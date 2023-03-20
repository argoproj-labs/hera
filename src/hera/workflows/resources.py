"""Holds the resource specification"""
from typing import Dict, Optional, Union

from pydantic import root_validator

from hera.shared._base_model import BaseModel as _BaseModel
from hera.workflows.models import ResourceRequirements as _ModelResourceRequirements
from hera.workflows.validators import validate_storage_units


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


class Resources(_BaseModel):
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
    ephemeral_request: Optional[str] = None
        The amount of ephemeral storage to request.
    ephemeral_limit: Optional[str] = None
        The emphemeral storage limit of the pod.
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
    ephemeral_request: Optional[str] = None
    ephemeral_limit: Optional[str] = None
    gpus: Optional[int] = None
    gpu_flag: Optional[str] = "nvidia.com/gpu"
    custom_resources: Optional[Dict] = None

    @root_validator(pre=True)
    def _check_specs(cls, values):
        cpu_request: Optional[Union[float, int, str]] = values.get("cpu_request")
        cpu_limit: Optional[Union[float, int, str]] = values.get("cpu_limit")
        memory_request: Optional[str] = values.get("memory_request")
        memory_limit: Optional[str] = values.get("memory_limit")
        ephemeral_request: Optional[str] = values.get("ephemeral_request")
        ephemeral_limit: Optional[str] = values.get("ephemeral_limit")

        if memory_request is not None:
            validate_storage_units(memory_request)
        if memory_limit is not None:
            validate_storage_units(memory_limit)

        if ephemeral_request is not None:
            validate_storage_units(ephemeral_request)
        if ephemeral_limit:
            validate_storage_units(ephemeral_limit)

        # TODO: add validation for CPU units if str
        if cpu_limit is not None and isinstance(cpu_limit, int):
            assert cpu_limit >= 0, "CPU limit must be positive"
        if cpu_request is not None and isinstance(cpu_request, int):
            assert cpu_request >= 0, "CPU request must be positive"
            if cpu_limit is not None and isinstance(cpu_limit, int):
                assert cpu_request <= cpu_limit, "CPU request must be smaller or equal to limit"

        return values

    def build(self) -> _ModelResourceRequirements:
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
