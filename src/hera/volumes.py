import uuid
from enum import Enum
from typing import List, Optional

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


class AccessMode(Enum):
    """A representations of the volume access modes for Kubernetes.

    Notes
    -----
        See https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes for more information.
    """

    ReadWriteOnce = "ReadWriteOnce"
    """the volume can be mounted as read-write by a single node. ReadWriteOnce access mode still can allow multiple
    pods to access the volume when the pods are running on the same node."""

    ReadOnlyMany = "ReadOnlyMany"
    """the volume can be mounted as read-only by many nodes"""

    ReadWriteMany = "ReadWriteMany"
    """the volume can be mounted as read-write by many nodes"""

    ReadWriteOncePod = "ReadWriteOncePod"
    """the volume can be mounted as read-write by a single Pod. Use ReadWriteOncePod access mode if you want to
    ensure that only one pod across whole cluster can read that PVC or write to it. This is only supported for CSI
    volumes and Kubernetes version 1.22+"""


class BaseVolume(BaseModel):
    """Base representation of a volume.

    Attributes
    ----------
    name: Optional[str]
        The name of the volume. One will be generated if the name is not specified. It is recommended to not pass a
        name to avoid any potential naming conflicts with existing empty dir volumes.
    mount_path: str
        The mounting point in the task e.g /mnt/my_path.
    """

    name: Optional[str]
    mount_path: str

    @validator('name', always=True)
    def check_name(cls, value):
        """Validates that a name is specified. If not, it sets it"""
        if not value:
            return str(uuid.uuid4())
        return value

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task"""
        raise NotImplementedError

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks"""
        raise NotImplementedError


class EmptyDirVolume(BaseVolume):
    """A representation of an in-memory empty dir volume.

    When mounted, this volume results in the creation of a temporary filesystem (tmpfs). The mount path will map to
    the memory location where files in the path are stored. The memory footprint/availability is equivalent to half
    the size of the node a workflow mounting an empty dir volume is mounted on, or limited by the size specification
    if one is passed.

    Attributes
    ----------
    size: str
        The size of the volume to create and mount, typically in gigabytes e.g 20Gi, 100Gi, 1Ti.
    """

    # default to empty size spec to allow for unlimited memory consumption
    size: str = ''
    # default to /dev/shm since it represents the shared memory concept in Unix systems
    mount_path: str = '/dev/shm'

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
        """Constructs and returns an Argo volume mount representation for tasks"""
        return VolumeMount(mount_path=self.mount_path, name=self.name)


class ExistingVolume(BaseVolume):
    """A representation of an existing volume. This can be used to mount existing volumes to workflow tasks"""

    @validator('name', always=True)
    def check_name(cls, value):
        """Verifies that the specified name does not contain underscores, which are not RFC1123 compliant"""
        assert '_' not in value, 'existing volume name cannot contain underscores, see RFC1123'
        return value

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task"""
        claim = PersistentVolumeClaimVolumeSource(claim_name=self.name)
        return ArgoVolume(name=self.name, persistent_volume_claim=claim)

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks"""
        return VolumeMount(name=self.name, mount_path=self.mount_path)


class SecretVolume(BaseVolume):
    """A volume representing a secret. This can be used to mount secrets to paths inside a task

    Attributes
    ----------
    secret_name: str
        The name of the secret existing in the task namespace
    """

    secret_name: str

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for a secret in the task namespace"""
        secret = SecretVolumeSource(secret_name=self.secret_name)
        return ArgoVolume(name=self.name, secret=secret)

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks"""
        return VolumeMount(name=self.name, mount_path=self.mount_path)


class ConfigMapVolume(BaseVolume):
    """A volume representing a config map. This can be used to mount config maps to paths inside a task

    Attributes
    ----------
    config_map_name: str
        The name of the config map existing in the task namespace.
    """

    config_map_name: str

    def get_volume(self) -> ArgoVolume:
        """Constructs an Argo volume representation for a config map in the task namespace"""
        config_map = ConfigMapVolumeSource(name=self.config_map_name)
        return ArgoVolume(name=self.name, config_map=config_map)

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks"""
        return VolumeMount(name=self.name, mount_path=self.mount_path)


class Volume(BaseVolume):
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
    access

    Raises
    ------
    ValueError or AssertionError upon failure to validate the units of the size. See
    `hera.v1.validators.validate_storage_units`.

    Notes
    -----
    A volume can only be mounted using one access mode at a time, even if it supports many. For example, a
    GCEPersistentDisk can be mounted as ReadWriteOnce by a single node or ReadOnlyMany by many nodes, but not at
    the same time.
    """

    size: str
    storage_class_name: str = 'standard'
    # note that different cloud providers support different types of access modes
    access_modes: List[AccessMode] = [AccessMode.ReadWriteOnce]

    class Config:
        use_enum_values = True

    @validator('size')
    def valid_units(cls, value):
        """Validates the storage units of the volume size"""
        validate_storage_units(value)
        return value

    def get_mount(self) -> VolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks"""
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
            access_modes=[am.value if isinstance(am, AccessMode) else am for am in self.access_modes],
            resources=ResourceRequirements(
                requests={
                    'storage': self.size,
                }
            ),
            storage_class_name=self.storage_class_name,
        )
        metadata = ObjectMeta(name=self.name)
        return PersistentVolumeClaim(spec=spec, metadata=metadata)
