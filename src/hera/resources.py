"""Holds the resource specification"""
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, root_validator, validator

from hera.validators import validate_storage_units
from hera.volumes import BaseVolume, EmptyDirVolume


class Resources(BaseModel):
    """A representation of a collection of resources that are requested to be consumed by a task for execution.

    Attributes
    ----------
    min_cpu: Union[int, float] = 1
        The minimum amount of CPU to request.
    max_cpu: Optional[Union[int, float]] = None
        The maximum amount of CPU to request. If this is not specified it's automatically set to min_cpu when
        `overwrite_maxs` is True.
    min_mem: str = '4Gi'
        The minimum amount of memory to request.
    max_mem: Optional[str]
        The maximum amount of memory to request. If this is not specified it's automatically set to min_mem when
        `overwrite_maxs` is True.
    gpus: Optional[int]
        The number of GPUs to request as part of the workflow.
    volumes: Optional[List[BaseVolume]] = None
        List of available Hera volumes [ConfigMapVolume, EmptyDirVolume, ExistingVolume, SecretVolume, Volume].
    overwrite_maxs: bool = True
        Whether to override `max_cpu` and `max_mem` with corresponding min values when they are not specified.
    """

    min_cpu: Union[int, float] = 1
    max_cpu: Optional[Union[int, float]] = None

    min_mem: str = '4Gi'
    max_mem: Optional[str] = None

    gpus: Optional[int] = None

    volumes: Optional[List[BaseVolume]] = None

    overwrite_maxs: bool = True

    @validator('min_mem', 'max_mem')
    def valid_units(cls, value):
        """Validates that memory specifications have correct units"""
        validate_storage_units(value)
        return value

    @validator('volumes')
    def valid_volume_frequencies(cls, value):
        """Validates that a single EmptyDir volume is specified (K8S limitation)"""
        freqs: Dict[str, int] = {}
        if value:
            for volume in value:
                if volume.__class__.__name__ in freqs:
                    freqs[volume.__class__.__name__] += 1
                else:
                    freqs[volume.__class__.__name__] = 1
                if volume.__class__ == EmptyDirVolume:
                    assert (
                        EmptyDirVolume.__class__.__name__ not in freqs or freqs[EmptyDirVolume.__class__.__name__] <= 1
                    )
        return value

    @root_validator
    def valid_values(cls, values):
        """Validates that cpu values are valid"""
        assert values['min_cpu'] >= 0, 'cannot specify a negative value for the min CPU field'

        if values.get('max_cpu') is None and values['overwrite_maxs']:
            values['max_cpu'] = values.get('min_cpu')

        if 'max_cpu' in values and values.get('max_cpu'):
            assert values['min_cpu'] <= values['max_cpu'], 'cannot specify a min CPU value smaller than max CPU'

        if values.get('max_mem') is None and values['overwrite_maxs']:
            values['max_mem'] = values.get('min_mem')
        return values
