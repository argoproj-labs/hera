import uuid
from typing import Optional

from argo_workflows.models import (
    ConfigMapVolumeSource,
    EmptyDirVolumeSource,
    ObjectMeta,
    PersistentVolumeClaim,
    PersistentVolumeClaimSpec,
    PersistentVolumeClaimVolumeSource,
    ResourceRequirements,
    SecretVolumeSource,
)
from argo_workflows.models import Volume as ArgoVolume
from argo_workflows.models import VolumeMount
from pydantic import BaseModel, validator

from hera.validators import validate_storage_units


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

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task.

        Returns
        -------
        Volume
            The volume representation that can be mounted in workflow steps/tasks.
        """
        size_limit = self.size if self.size else ""
        empty_dir = EmptyDirVolumeSource(medium='Memory', size_limit=size_limit)
        return ArgoVolume(name=self.name, empty_dir=empty_dir)

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks.

        Returns
        -------
        VolumeMount
            The Argo model for mounting volumes.
        """
        return VolumeMount(mount_path=self.mount_path, name=self.name)


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

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task.

        Returns
        -------
        _ArgoVolume
            The volume representation that can be mounted in workflow steps/tasks.
        """
        claim = PersistentVolumeClaimVolumeSource(claim_name=self.name)
        return ArgoVolume(name=self.name, persistent_volume_claim=claim)

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks.

        Returns
        -------
        V1VolumeMount
            The Argo model for mounting volumes.
        """
        return VolumeMount(name=self.name, mount_path=self.mount_path)


class SecretVolume(BaseModel):
    """A volume representing a secret. This can be used to mount secrets to paths inside a task

    Attributes
    ----------
    name: Optional[str]
        The name of the volume, if not supplied a unique id will be generated for the name
    secret_name: str
        The name of the secret existing in the task namespace
    mount_path: str
        The mounting point in the task e.g /mnt/my_path. The secrets will be mounted to this path, with the names
        being used as file names, and the values in those files
    """

    name: Optional[str] = None
    secret_name: str
    mount_path: str

    @validator('name', always=True)
    def check_name(cls, value):
        """Validates that a name is specified. If not, it sets it"""
        if not value:
            return str(uuid.uuid4())
        return value

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for a secret in the task namespace

        Returns
        -------
        ArgoVolume
            The volume representation that can be mounted in workflow steps/tasks.
        """
        secret = SecretVolumeSource(secret_name=self.secret_name)
        return ArgoVolume(name=self.name, secret=secret)

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks.

        Returns
        -------
        VolumeMount
            The Argo model for mounting volumes.
        """
        return VolumeMount(name=self.name, mount_path=self.mount_path)


class ConfigMapVolume(BaseModel):
    """A volume representing a config map. This can be used to mount config maps to paths inside a task

    Attributes
    ----------
    name: Optional[str]
        The name of the volume, if not supplied a unique id will be generated for the name
    config_map_name: str
        The name of the config map existing in the task namespace
    mount_path: str
        The mounting point in the task e.g /mnt/my_path. The config map will be mounted to this path, with the keys
        being used as file names, and the values in those files
    """

    name: Optional[str] = None
    config_map_name: str
    mount_path: str

    @validator('name', always=True)
    def check_name(cls, value):
        """Validates that a name is specified. If not, it sets it"""
        if not value:
            return str(uuid.uuid4())
        return value

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for a config map in the task namespace

        Returns
        -------
        ArgoVolume
            The volume representation that can be mounted in workflow steps/tasks.
        """
        config_map = ConfigMapVolumeSource(name=self.config_map_name)
        return ArgoVolume(name=self.name, config_map=config_map)

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks.

        Returns
        -------
        VolumeMount
            The Argo model for mounting volumes.
        """
        return VolumeMount(name=self.name, mount_path=self.mount_path)


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
        VolumeMount
            The Argo model for mounting volumes.
        """
        return VolumeMount(mount_path=self.mount_path, name=self.name)

    def get_claim_spec(self) -> PersistentVolumeClaim:
        """Constructs and returns an Argo volume claim representation for tasks. This is typically used by workflows
        to dynamically provision volumes and discard them upon completion.

        Returns
        -------
        PersistentVolumeClaim
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
