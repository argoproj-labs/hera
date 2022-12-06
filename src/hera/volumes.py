import uuid
from dataclasses import dataclass, field
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
from argo_workflows.models import VolumeDevice as ArgoVolumeDevice
from argo_workflows.models import VolumeMount as ArgoVolumeMount

from hera.validators import validate_storage_units


@dataclass
class _NamedConfigMap:
    config_map_name: str


@dataclass
class _NamedSecret:
    secret_name: str


class AccessMode(str, Enum):
    """A representations of the volume access modes for Kubernetes.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes for more information.
    """

    ReadWriteOnce = "ReadWriteOnce"
    """
    The volume can be mounted as read-write by a single node. ReadWriteOnce access mode still can allow multiple
    pods to access the volume when the pods are running on the same node
    """

    ReadOnlyMany = "ReadOnlyMany"
    """The volume can be mounted as read-only by many nodes"""

    ReadWriteMany = "ReadWriteMany"
    """The volume can be mounted as read-write by many nodes"""

    ReadWriteOncePod = "ReadWriteOncePod"
    """
    The volume can be mounted as read-write by a single Pod. Use ReadWriteOncePod access mode if you want to
    ensure that only one pod across whole cluster can read that PVC or write to it. This is only supported for CSI
    volumes and Kubernetes version 1.22+.
    """

    def __str__(self):
        return str(self.value)


# `@dataclass` doesn't support adding required fields after optional ones. This is
# particularly challenging when a subclass would like to add additional required fields,
# as is the case with `Volume.size` being required (but not set in `_BaseVolume`). To
# work around this, we can split up the *arg/required parameters from the
# **kwarg/optional ones into separate base classes. Then, subclasses can inherit with
# the keyword baseclass coming before the positional one (`@dataclass` collects fields
# in reverse MRO order) and inject a mixin class between them that introduces new
# required fields. They should still inherit from `_BaseVolume` as the first base class
# in order to include the methods.


@dataclass
class _BaseVolumePositional:
    mount_path: str


@dataclass
class _BaseVolumeKeyword:
    name: Optional[str] = None
    sub_path: Optional[str] = None


@dataclass
class _BaseVolume(_BaseVolumeKeyword, _BaseVolumePositional):
    """Base representation of a volume.

    Attributes
    ----------
    name: Optional[str]
        The name of the volume. One will be generated if the name is not specified. It is recommended to not pass a
        name to avoid any potential naming conflicts with existing empty dir volumes.
    mount_path: str
        The mounting point in the task e.g /mnt/my_path.
    sub_path: str
        Path within the volume from which the container's volume should be mounted.
    """

    def __post_init__(self):
        if self.name is None:
            self.name = str(uuid.uuid4())

    def _build_claim_spec(self):
        return None

    def _build_mount(self) -> ArgoVolumeMount:
        """Constructs and returns an Argo volume mount representation for tasks"""
        vm = ArgoVolumeMount(name=self.name, mount_path=self.mount_path)
        if self.sub_path:
            setattr(vm, "sub_path", self.sub_path)
        return vm


@dataclass
class _Sized:
    size: str


@dataclass
class VolumeMount(_BaseVolume):
    """A base representation of volume mount

    Attributes
    ----------
    name: Optional[str]
        The name of the volume. One will be generated if the name is not specified. It is recommended to not pass a
        name to avoid any potential naming conflicts with existing empty dir volumes.
    mount_path: str
        The mounting point in the task e.g /mnt/my_path.
    sub_path: str
        Path within the volume from which the container's volume should be mounted.
    mount_propagation: Optional[str] = None
        Determines how mounts are propagated from the host to container and the other way around.
    read_only: bool = False
        Mounted read-only if true, read-write otherwise.
    sub_path_expr: Optional[str] = ""
        Expanded path within the volume from which the container's volume should be mounted. Behaves similarly to
        `sub_path` but environment variable references $(VAR_NAME) are expanded using the container's
        environment. Mutually exclusive with `sub_path`.
    """

    mount_propagation: Optional[str] = None
    read_only: Optional[bool] = None
    sub_path_expr: Optional[str] = None

    def __post_init__(self) -> None:
        if self.sub_path is not None and self.sub_path_expr is None:
            raise ValueError("`sub_path` and `sub_path_expr` are mutually exclusive")
        if self.sub_path_expr is not None and self.sub_path is None:
            raise ValueError("`sub_path_expr` and `sub_path` are mutually exclusive")
        if self.name is None:
            self.name = str(uuid.uuid4())

    def _build_mount(self) -> ArgoVolumeMount:
        volume = ArgoVolumeMount(self.mount_path, self.name)
        if self.mount_propagation is not None:
            setattr(volume, "mount_propagation", self.mount_propagation)
        if self.read_only is not None:
            setattr(volume, "read_only", self.read_only)
        if self.sub_path is not None:
            setattr(volume, "sub_path", self.sub_path)
        if self.sub_path_expr is not None:
            setattr(volume, "sub_path_expr", self.sub_path_expr)
        return volume


@dataclass
class VolumeDevice:
    """Volume device representation.

    Parameters
    ----------
    name: Optional[str] = None
        Name of the persistent volume claim to map.
    device_path: str
        Path inside the container that the device will be mapped to.
    """

    def __init__(self, name: str, device_path: str) -> None:
        self.name = name
        self.device_path = device_path

    def build(self) -> ArgoVolumeDevice:
        return ArgoVolumeDevice(self.device_path, self.name)


@dataclass
class EmptyDirVolume(_BaseVolume):
    """A representation of an in-memory empty dir volume.

    When mounted, this volume results in the creation of a temporary filesystem (tmpfs). The mount path will map to
    the memory location where files in the path are stored. The memory footprint/availability is equivalent to half
    the size of the node a workflow mounting an empty dir volume is mounted on, or limited by the size specification
    if one is passed.
    """

    # default to /dev/shm since it represents the shared memory concept in Unix systems
    mount_path: str = "/dev/shm"
    size: Optional[str] = None

    def _build_claim_spec(self) -> ArgoVolume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task.

        Returns
        -------
        ArgoVolume
            The volume representation that can be mounted in workflow steps/tasks.
        """
        if self.size is not None:
            return ArgoVolume(name=self.name, empty_dir=EmptyDirVolumeSource(medium="Memory", size_limit=self.size))
        else:
            return ArgoVolume(name=self.name, empty_dir=EmptyDirVolumeSource(medium="Memory"))


@dataclass
class ExistingVolume(_BaseVolume):
    """A representation of an existing volume. This can be used to mount existing volumes to workflow tasks"""

    def __post_init__(self):
        assert self.name, "ExistingVolume needs a name to use as claim name"
        # super().__post_init__()
        self._check_name()

    def _check_name(self):
        """Verifies that the specified name does not contain underscores, which are not RFC1123 compliant"""
        assert self.name
        assert "_" not in self.name, "existing volume name cannot contain underscores, see RFC1123"

    def _build_claim_spec(self) -> ArgoVolume:
        """Constructs an Argo volume representation for mounting existing volumes to a step/task"""
        claim = PersistentVolumeClaimVolumeSource(claim_name=self.name)
        return ArgoVolume(name=self.name, persistent_volume_claim=claim)


@dataclass
class SecretVolume(_BaseVolume, _NamedSecret):
    """A volume representing a secret. This can be used to mount secrets to paths inside a task

    Attributes
    ----------
    secret_name: str
        The name of the secret existing in the task namespace
    """

    def _build_claim_spec(self) -> ArgoVolume:
        """Constructs an Argo volume representation for a secret in the task namespace"""
        secret = SecretVolumeSource(secret_name=self.secret_name)
        # TODO: Do we want the name to be the same as secret_name to bundle objects?
        return ArgoVolume(name=self.name, secret=secret)


@dataclass
class ConfigMapVolume(_BaseVolume, _NamedConfigMap):
    """A volume representing a config map. This can be used to mount config maps to paths inside a task

    Attributes
    ----------
    config_map_name: str
        The name of the config map existing in the task namespace.
    """

    def _build_claim_spec(self) -> ArgoVolume:
        """Constructs an Argo volume representation for a config map in the task namespace"""
        config_map = ConfigMapVolumeSource(name=self.config_map_name)
        return ArgoVolume(name=self.name, config_map=config_map)


@dataclass
class Volume(_BaseVolume, _BaseVolumeKeyword, _Sized, _BaseVolumePositional):
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

    Notes
    -----
    A volume can only be mounted using one access mode at a time, even if it supports many. For example, a
    GCEPersistentDisk can be mounted as ReadWriteOnce by a single node or ReadOnlyMany by many nodes, but not at
    the same time.
    """

    storage_class_name: str = "standard"
    # note that different cloud providers support different types of access modes
    access_modes: List[AccessMode] = field(default_factory=lambda: [AccessMode.ReadWriteOnce])
    sub_path: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        validate_storage_units(self.size)
        for mode in self.access_modes:
            assert isinstance(mode, AccessMode)

    def _build_claim_spec(self) -> PersistentVolumeClaim:
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
                    "storage": self.size,
                }
            ),
            storage_class_name=self.storage_class_name,
        )
        metadata = ObjectMeta(name=self.name)
        return PersistentVolumeClaim(spec=spec, metadata=metadata)
