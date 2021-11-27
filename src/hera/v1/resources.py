"""Holds the resource specification"""
from typing import Optional, Union

from pydantic import BaseModel, root_validator, validator

from hera.v1.empty_dir_volume import EmptyDirVolume
from hera.v1.existing_volume import ExistingVolume
from hera.v1.validators import validate_storage_units
from hera.v1.volume import Volume


class Resources(BaseModel):
    """A representation of a collection of resources that are requested to be consumed by a task for execution.

    Attributes
    ----------
    min_cpu: Union[int, float] = 1
        The minimum amount of CPU to request.
    max_cpu: Union[int, float] = None
        The maximum amount of CPU to request. If this is not specified it's automatically set to min_cpu.
    min_mem: str = '4Gi'
        The minimum amount of memory to request.
    max_mem: Optional[str]
        The maximum amount of memory to request. If this is not specified it's automatically set to min_mem.
    gpus: Optional[int]
        The number of GPUs to request as part of the workflow.
    volumes: Optional[Volume]
        The volumes to dynamically provision.
    """

    min_cpu: Union[int, float] = 1
    max_cpu: Union[int, float] = None

    min_mem: str = '4Gi'
    max_mem: Optional[str] = None

    gpus: Optional[int] = None

    volume: Optional[Volume] = None
    existing_volume: Optional[ExistingVolume] = None
    empty_dir_volume: Optional[EmptyDirVolume] = None

    @validator('min_mem', 'max_mem')
    def valid_units(cls, value):
        """Validates that memory specifications have correct units"""
        validate_storage_units(value)
        return value

    @root_validator
    def valid_values(cls, values):
        """Validates that cpu values are valid"""
        assert values['min_cpu'] >= 0, 'cannot specify a negative value for the min CPU field'
        if 'max_cpu' in values and values.get('max_cpu'):
            assert values['min_cpu'] <= values['max_cpu'], 'cannot specify a min CPU value smaller than max CPU'
        return values
