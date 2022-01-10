"""Holds the existing volume specification"""
from argo.workflows.client import (
    V1PersistentVolumeClaimVolumeSource,
    V1Volume,
    V1VolumeMount,
)
from pydantic import BaseModel, validator


class ExistingVolume(BaseModel):
    """A representation of an existing volume. This can be used to mount existing volumes to workflow steps and tasks.

    Attributes
    ----------
    name: str
        The name of the existing volume claim. This is assumed to be a valid name of an already existing volume
        provisioned in the K8S cluster the Argo server is running in. In addition, it is assumed the volume is
        mounted via an IP, which makes it available across regions and zones in K8S clusters.
    mount_path: str
        The mounting point in the task e.g /mnt/my_path.
    """

    name: str
    mount_path: str

    @validator('name', always=True)
    def check_name(cls, value):
        """Verifies that the specified name does not contain underscores, which are not RFC1123 compliant"""
        assert '_' not in value, 'existing volume name cannot contain underscores, see RFC1123'
        return value

    def get_volume(self) -> V1Volume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task.

        Returns
        -------
        V1Volume
            The volume representation that can be mounted in workflow steps/tasks.
        """
        claim = V1PersistentVolumeClaimVolumeSource(claim_name=self.name)
        return V1Volume(name=self.name, persistent_volume_claim=claim)

    def get_mount(self) -> V1VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks.

        Returns
        -------
        V1VolumeMount
            The Argo model for mounting volumes.
        """
        return V1VolumeMount(name=self.name, mount_path=self.mount_path)
