import uuid
from typing import Optional

from argo_workflows.models import (
    ObjectMeta,
    PersistentVolumeClaim,
    PersistentVolumeClaimSpec,
    ResourceRequirements,
    VolumeMount,
)
from pydantic import BaseModel, validator

from hera.v1.validators import validate_storage_units


class Volume(BaseModel):
    """A dynamically created and mountable volume representation.

    This is used to specify a volume mount for a particular task to be executed. It is recommended to not pass in a
    name as the name can be auto-generated by uuid.uuid4(). This allows the volume to get a unique name that can then
    be mounted, uniquely, by the task on which the volume was specified.

    Attributes
    ----------
    size: str
        The size of the volume to create and mount, typically in gigabytes e.g 20Gi, 100Gi, 1Ti.
    mount_path: str
        The mounting point in the task e.g /mnt/my_path.
    storage_class_name: str = 'standard'
        The name of the storage class name to use when provisioning volumes. See
        https://kubernetes.io/docs/concepts/storage/storage-classes/ for more information.
    name: Optional[str]
        The name of the volume. One will be generated if the name is not specified. It is recommended to not pass a
        name to avoid any potential naming conflicts with existing volumes.

    Raises
    ------
    ValueError or AssertionError upon failure to validate the units of the size. See
    `hera.v1.validators.validate_storage_units`.
    """

    size: str
    mount_path: str
    storage_class_name: str = 'standard'
    name: Optional[str]

    @validator('name', always=True)
    def check_name(cls, value):
        """Validates that a name is specified. If not, it sets it"""
        if not value:
            return str(uuid.uuid4())
        return value

    @validator('size')
    def valid_units(cls, value):
        """Validates the storage units of the volume size"""
        validate_storage_units(value)
        return value

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks.

        Returns
        -------
        V1VolumeMount
            The Argo model for mounting volumes.
        """
        return VolumeMount(mount_path=self.mount_path, name=self.name)

    def get_claim_spec(self) -> PersistentVolumeClaim:
        """Constructs and returns an Argo volume claim representation for tasks. This is typically used by workflows
        to dynamically provision volumes and discard them upon completion.

        Returns
        -------
        V1PersistentVolumeClaim
            The claim to be used by the Argo workflow.
        """
        spec = PersistentVolumeClaimSpec(
            # GKE does not accept ReadWriteMany for dynamically provisioned disks, default to ReadWriteOnce
            access_modes=['ReadWriteOnce'],
            resources=ResourceRequirements(
                requests={
                    'storage': self.size,
                }
            ),
            storage_class_name=self.storage_class_name,
        )
        metadata = ObjectMeta(name=self.name)
        return PersistentVolumeClaim(spec=spec, metadata=metadata)
