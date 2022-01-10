"""Holds the empty directory volume object"""
import uuid
from typing import Optional

from argo.workflows.client import V1EmptyDirVolumeSource, V1Volume, V1VolumeMount
from pydantic import BaseModel, validator


class EmptyDirVolume(BaseModel):
    """A representation of an in-memory empty dir volume.

    When mounted, this volume results in the creation of a temporary filesystem (tmpfs). The mount path will map to
    the memory location where files in the path are stored. The memory footprint/availability is equivalent to half
    the size of the node a workflow mounting an empty dir volume is mounted on, or limited by the size specification
    if one is passed.

    Attributes
    ----------
    name: Optional[str]
        The name of the volume. One will be generated if the name is not specified. It is recommended to not pass a
        name to avoid any potential naming conflicts with existing empty dir volumes.
    size: str
        The size of the volume to create and mount, typically in gigabytes e.g 20Gi, 100Gi, 1Ti.
    mount_path: str
        The mounting point in the task e.g /mnt/my_path.
    """

    name: Optional[str]
    # default to empty size spec to allow for unlimited memory consumption
    size: str = ''
    # default to /dev/shm since it represents the shared memory concept in Unix systems
    mount_path: str = '/dev/shm'

    @validator('name', always=True)
    def check_name(cls, value):
        """Validates that a name is specified. If not, it sets it"""
        if not value:
            return str(uuid.uuid4())
        return value

    def get_volume(self) -> V1Volume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task.

        Returns
        -------
        V1Volume
            The volume representation that can be mounted in workflow steps/tasks.
        """
        size_limit = self.size if self.size else None
        empty_dir = V1EmptyDirVolumeSource(medium='Memory', size_limit=size_limit)
        return V1Volume(name=self.name, empty_dir=empty_dir)

    def get_mount(self) -> V1VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks.

        Returns
        -------
        V1VolumeMount
            The Argo model for mounting volumes.
        """
        return V1VolumeMount(mount_path=self.mount_path, name=self.name)
