"""The `hera.workflows.volume` module provides all Argo volume types that can be used via Hera."""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, cast

from hera.workflows.models import (
    AWSElasticBlockStoreVolumeSource as _ModelAWSElasticBlockStoreVolumeSource,
    AzureDiskVolumeSource as _ModelAzureDiskVolumeSource,
    AzureFileVolumeSource as _ModelAzureFileVolumeSource,
    CephFSVolumeSource as _ModelCephFSVolumeSource,
    CinderVolumeSource as _ModelCinderVolumeSource,
    ConfigMapVolumeSource as _ModelConfigMapVolumeSource,
    CSIVolumeSource as _ModelCSIVolumeSource,
    DownwardAPIVolumeSource as _ModelDownwardAPIVolumeSource,
    EmptyDirVolumeSource as _ModelEmptyDirVolumeSource,
    EphemeralVolumeSource as _ModelEphemeralVolumeSource,
    FCVolumeSource as _ModelFCVolumeSource,
    FlexVolumeSource as _ModelFlexVolumeSource,
    FlockerVolumeSource as _ModelFlockerVolumeSource,
    GCEPersistentDiskVolumeSource as _ModelGCEPersistentDiskVolumeSource,
    GitRepoVolumeSource as _ModelGitRepoVolumeSource,
    GlusterfsVolumeSource as _ModelGlusterfsVolumeSource,
    HostPathVolumeSource as _ModelHostPathVolumeSource,
    ISCSIVolumeSource as _ModelISCSIVolumeSource,
    NFSVolumeSource as _ModelNFSVolumeSource,
    ObjectMeta,
    PersistentVolumeClaim as _ModelPersistentVolumeClaim,
    PersistentVolumeClaimSpec as _ModelPersistentVolumeClaimSpec,
    PersistentVolumeClaimVolumeSource as _ModelPersistentVolumeClaimVolumeSource,
    PhotonPersistentDiskVolumeSource as _ModelPhotonPersistentDiskVolumeSource,
    PortworxVolumeSource as _ModelPortworxVolumeSource,
    ProjectedVolumeSource as _ModelProjectedVolumeSource,
    QuobyteVolumeSource as _ModelQuobyteVolumeSource,
    RBDVolumeSource as _ModelRBDVolumeSource,
    ScaleIOVolumeSource as _ModelScaleIOVolumeSource,
    SecretVolumeSource as _ModelSecretVolumeSource,
    StorageOSVolumeSource as _ModelStorageOSVolumeSource,
    Volume as _ModelVolume,
    VolumeMount as _ModelVolumeMount,
    VolumeResourceRequirements,
    VsphereVirtualDiskVolumeSource as _ModelVsphereVirtualDiskVolumeSource,
)
from hera.workflows.models.io.k8s.api.core.v1 import (
    DownwardAPIVolumeFile,
    KeyToPath,
    LocalObjectReference,
    PersistentVolumeClaimTemplate,
    TypedLocalObjectReference,
    TypedObjectReference,
    VolumeProjection,
)
from hera.workflows.models.io.k8s.apimachinery.pkg.api import resource
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta import v1
from hera.workflows.validators import validate_storage_units


class AccessMode(Enum):
    """A representations of the volume access modes for Kubernetes.

    Notes:
        See: [access modes docs](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes) for
        more information.
    """

    read_write_once = "ReadWriteOnce"
    """
    The volume can be mounted as read-write by a single node. ReadWriteOnce access mode still can allow multiple
    pods to access the volume when the pods are running on the same node
    """

    read_only_many = "ReadOnlyMany"
    """The volume can be mounted as read-only by many nodes"""

    read_write_many = "ReadWriteMany"
    """The volume can be mounted as read-write by many nodes"""

    read_write_once_pod = "ReadWriteOncePod"
    """
    The volume can be mounted as read-write by a single Pod. Use ReadWriteOncePod access mode if you want to
    ensure that only one pod across whole cluster can read that PVC or write to it. This is only supported for CSI
    volumes and Kubernetes version 1.22+.
    """

    def __str__(self) -> str:
        """Returns the value representation of the enum in the form of a string."""
        return str(self.value)


@dataclass(kw_only=True)
class _BaseVolume:
    """Base volume representation."""

    name: Optional[str] = None
    mount_path: Optional[str] = None
    mount_propagation: Optional[str] = None
    read_only: Optional[bool] = None
    recursive_read_only: Optional[str] = None
    sub_path: Optional[str] = None
    sub_path_expr: Optional[str] = None

    def __post_init__(self):
        if self.name is None:
            self.name = str(uuid.uuid4())

    def _build_persistent_volume_claim(self) -> _ModelPersistentVolumeClaim:
        raise NotImplementedError

    def _build_volume(self) -> _ModelVolume:
        raise NotImplementedError

    def _build_volume_mount(self) -> _ModelVolumeMount:
        assert self.name
        assert self.mount_path
        return _ModelVolumeMount(
            name=self.name,
            mount_path=self.mount_path,
            mount_propagation=self.mount_propagation,
            read_only=self.read_only,
            sub_path=self.sub_path,
            sub_path_expr=self.sub_path_expr,
        )


@dataclass(kw_only=True)
class AWSElasticBlockStoreVolume(_BaseVolume):
    """Representation of AWS elastic block store volume."""

    volume_id: str
    fs_type: Optional[str] = None
    partition: Optional[int] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            aws_elastic_block_store=_ModelAWSElasticBlockStoreVolumeSource(
                fs_type=self.fs_type, partition=self.partition, read_only=self.read_only, volume_id=self.volume_id
            ),
        )


@dataclass(kw_only=True)
class AzureDiskVolume(_BaseVolume):
    """Representation of an Azure disk volume."""

    caching_mode: Optional[str] = None
    disk_name: str
    disk_uri: str
    fs_type: Optional[str] = None
    kind: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            azure_disk=_ModelAzureDiskVolumeSource(
                caching_mode=self.caching_mode,
                disk_name=self.disk_name,
                disk_uri=self.disk_uri,
                fs_type=self.fs_type,
                kind=self.kind,
                read_only=self.read_only,
            ),
        )


@dataclass(kw_only=True)
class AzureFileVolume(_BaseVolume):
    """Representation of an Azure file that can be mounted as a volume."""

    secret_name: str
    share_name: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            azure_file=_ModelAzureFileVolumeSource(
                read_only=self.read_only, secret_name=self.secret_name, share_name=self.share_name
            ),
        )


@dataclass(kw_only=True)
class CephFSVolume(_BaseVolume):
    """Representation of a Ceph file system volume."""

    monitors: List[str]
    path: Optional[str] = None
    secret_file: Optional[str] = None
    secret_ref: Optional[LocalObjectReference] = None
    user: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            cephfs=_ModelCephFSVolumeSource(
                monitors=self.monitors,
                path=self.path,
                read_only=self.read_only,
                secret_file=self.secret_file,
                secret_ref=self.secret_ref,
                user=self.user,
            ),
        )


@dataclass(kw_only=True)
class CinderVolume(_BaseVolume):
    """Representation of a Cinder volume."""

    fs_type: Optional[str] = None
    secret_ref: Optional[LocalObjectReference] = None
    volume_id: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            cinder=_ModelCinderVolumeSource(
                fs_type=self.fs_type,
                read_only=self.read_only,
                secret_ref=self.secret_ref,
                volume_id=self.volume_id,
            ),
        )


@dataclass(kw_only=True)
class ConfigMapVolume(_BaseVolume):
    """Representation of a config map volume."""

    default_mode: Optional[int] = None
    items: Optional[List[KeyToPath]] = None
    optional: Optional[bool] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            config_map=_ModelConfigMapVolumeSource(
                default_mode=self.default_mode, items=self.items, name=self.name, optional=self.optional
            ),
        )


@dataclass(kw_only=True)
class CSIVolume(_BaseVolume):
    """Representation of a container service interface volume."""

    driver: str
    fs_type: Optional[str] = None
    node_publish_secret_ref: Optional[LocalObjectReference] = None
    volume_attributes: Optional[Dict[str, str]] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            csi=_ModelCSIVolumeSource(
                driver=self.driver,
                fs_type=self.fs_type,
                node_publish_secret_ref=self.node_publish_secret_ref,
                read_only=self.read_only,
                volume_attributes=self.volume_attributes,
            ),
        )


@dataclass(kw_only=True)
class DownwardAPIVolume(_BaseVolume):
    """Representation of a volume passed via the downward API."""

    default_mode: Optional[int] = None
    items: Optional[List[DownwardAPIVolumeFile]] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            downward_api=_ModelDownwardAPIVolumeSource(default_mode=self.default_mode, items=self.items),
        )


@dataclass(kw_only=True)
class EmptyDirVolume(_BaseVolume):
    """Representation of an empty dir volume from K8s."""

    medium: Optional[str] = None
    size_limit: Optional[resource.Quantity] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name, empty_dir=_ModelEmptyDirVolumeSource(medium=self.medium, size_limit=self.size_limit)
        )


@dataclass(kw_only=True)
class EphemeralVolume(_BaseVolume):
    """Representation of a volume that uses ephemeral storage shared with the K8s node a pod is scheduled on."""

    volume_claim_template: Optional[PersistentVolumeClaimTemplate] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name, ephemeral=_ModelEphemeralVolumeSource(volume_claim_template=self.volume_claim_template)
        )


@dataclass(kw_only=True)
class FCVolume(_BaseVolume):
    """An FV volume representation."""

    fs_type: Optional[str] = None
    lun: Optional[int] = None
    target_ww_ns: Optional[List[str]] = None
    wwids: Optional[List[str]] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            fc=_ModelFCVolumeSource(
                fs_type=self.fs_type,
                lun=self.lun,
                read_only=self.read_only,
                target_ww_ns=self.target_ww_ns,
                wwids=self.wwids,
            ),
        )


@dataclass(kw_only=True)
class FlexVolume(_BaseVolume):
    """A Flex volume representation."""

    driver: str
    fs_type: Optional[str] = None
    options: Optional[Dict[str, str]] = None
    secret_ref: Optional[LocalObjectReference] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            flex_volume=_ModelFlexVolumeSource(
                driver=self.driver,
                fs_type=self.fs_type,
                options=self.options,
                read_only=self.read_only,
                secret_ref=self.secret_ref,
            ),
        )


@dataclass(kw_only=True)
class FlockerVolume(_BaseVolume):
    """A Flocker volume representation."""

    dataset_name: Optional[str] = None
    dataset_uuid: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            flocker=_ModelFlockerVolumeSource(dataset_name=self.dataset_name, dataset_uuid=self.dataset_uuid),
        )


@dataclass(kw_only=True)
class GCEPersistentDiskVolume(_BaseVolume):
    """A representation of a Google Cloud Compute Enginer persistent disk.

    Notes:
        The volume must exist on GCE before a request to mount it to a pod is performed.
    """

    fs_type: Optional[str] = None
    partition: Optional[int] = None
    pd_name: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            gce_persistent_disk=_ModelGCEPersistentDiskVolumeSource(
                fs_type=self.fs_type, partition=self.partition, pd_name=self.pd_name, read_only=self.read_only
            ),
        )


@dataclass(kw_only=True)
class GitRepoVolume(_BaseVolume):
    """A representation of a Git repo that can be mounted as a volume."""

    directory: Optional[str] = None
    repository: str
    revision: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            git_repo=_ModelGitRepoVolumeSource(
                directory=self.directory, repository=self.repository, revision=self.revision
            ),
        )


@dataclass(kw_only=True)
class GlusterfsVolume(_BaseVolume):
    """A representation for a Gluster filesystem volume."""

    endpoints: str
    path: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            glusterfs=_ModelGlusterfsVolumeSource(endpoints=self.endpoints, path=self.path, read_only=self.read_only),
        )


@dataclass(kw_only=True)
class HostPathVolume(_BaseVolume):
    """Representation for a volume that can be mounted from a host path/node location."""

    path: str
    type: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(name=self.name, host_path=_ModelHostPathVolumeSource(path=self.path, type=self.type))


@dataclass(kw_only=True)
class ISCSIVolume(_BaseVolume):
    """Representation of ISCSI volume."""

    chap_auth_discovery: Optional[bool] = None
    chap_auth_session: Optional[bool] = None
    fs_type: Optional[str] = None
    initiator_name: Optional[str] = None
    iqn: str
    iscsi_interface: Optional[str] = None
    lun: int
    portals: Optional[List[str]] = None
    secret_ref: Optional[LocalObjectReference] = None
    target_portal: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            iscsi=_ModelISCSIVolumeSource(
                chap_auth_discovery=self.chap_auth_discovery,
                chap_auth_session=self.chap_auth_discovery,
                fs_type=self.fs_type,
                initiator_name=self.initiator_name,
                iqn=self.iqn,
                iscsi_interface=self.iscsi_interface,
                lun=self.lun,
                portals=self.portals,
                read_only=self.read_only,
                secret_ref=self.secret_ref,
                target_portal=self.target_portal,
            ),
        )


@dataclass(kw_only=True)
class NFSVolume(_BaseVolume):
    """A network file system volume representation."""

    path: str
    server: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name, nfs=_ModelNFSVolumeSource(server=self.server, path=self.path, read_only=self.read_only)
        )


@dataclass(kw_only=True)
class PhotonPersistentDiskVolume(_BaseVolume):
    """A Photon Persistent Disk representation."""

    fs_type: Optional[str] = None
    pd_id: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            photon_persistent_disk=_ModelPhotonPersistentDiskVolumeSource(fs_type=self.fs_type, pd_id=self.pd_id),
        )


@dataclass(kw_only=True)
class PortworxVolume(_BaseVolume):
    """`PortworxVolume` represents a Portworx volume to mount to a container."""

    fs_type: Optional[str] = None
    volume_id: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            portworx_volume=_ModelPortworxVolumeSource(
                fs_type=self.fs_type, read_only=self.read_only, volume_id=self.volume_id
            ),
        )


@dataclass(kw_only=True)
class ProjectedVolume(_BaseVolume):
    """`ProjectedVolume` represents a projected volume to mount to a container."""

    default_mode: Optional[int] = None
    sources: Optional[List[VolumeProjection]] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name, projected=_ModelProjectedVolumeSource(default_mode=self.default_mode, sources=self.sources)
        )


@dataclass(kw_only=True)
class QuobyteVolume(_BaseVolume):
    """`QuobyteVolume` represents a Quobyte volume to mount to a container."""

    group: Optional[str] = None
    registry: str
    tenant: Optional[str] = None
    user: Optional[str] = None
    volume: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            quobyte=_ModelQuobyteVolumeSource(
                group=self.group,
                read_only=self.read_only,
                registry=self.registry,
                tenant=self.tenant,
                user=self.user,
                volume=self.volume,
            ),
        )


@dataclass(kw_only=True)
class RBDVolume(_BaseVolume):
    """An RDB volume representation."""

    fs_type: Optional[str] = None
    image: str
    keyring: Optional[str] = None
    monitors: List[str]
    pool: Optional[str] = None
    secret_ref: Optional[LocalObjectReference] = None
    user: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            rbd=_ModelRBDVolumeSource(
                fs_type=self.fs_type,
                image=self.image,
                keyring=self.keyring,
                monitors=self.monitors,
                pool=self.pool,
                read_only=self.read_only,
                secret_ref=self.secret_ref,
                user=self.user,
            ),
        )


@dataclass(kw_only=True)
class ScaleIOVolume(_BaseVolume):
    """`ScaleIOVolume` represents a ScaleIO volume to mount to the container."""

    fs_type: Optional[str] = None
    gateway: str
    protection_domain: Optional[str] = None
    secret_ref: LocalObjectReference
    ssl_enabled: Optional[bool] = None
    storage_mode: Optional[str] = None
    storage_pool: Optional[str] = None
    system: str
    volume_name: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            scale_io=_ModelScaleIOVolumeSource(
                fs_type=self.fs_type,
                gateway=self.gateway,
                protection_domain=self.protection_domain,
                read_only=self.read_only,
                secret_ref=self.secret_ref,
                ssl_enabled=self.ssl_enabled,
                storage_mode=self.storage_mode,
                storage_pool=self.storage_pool,
                system=self.system,
                volume_name=self.volume_name,
            ),
        )


@dataclass(kw_only=True)
class SecretVolume(_BaseVolume):
    """`SecretVolume` supports mounting a K8s secret as a container volume."""

    default_mode: Optional[int] = None
    items: Optional[List[KeyToPath]] = None
    optional: Optional[bool] = None
    secret_name: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            secret=_ModelSecretVolumeSource(
                default_mode=self.default_mode, items=self.items, optional=self.optional, secret_name=self.secret_name
            ),
        )


@dataclass(kw_only=True)
class StorageOSVolume(_BaseVolume):
    """`StorageOSVolume` represents a Storage OS volume to mount."""

    fs_type: Optional[str] = None
    secret_ref: Optional[LocalObjectReference] = None
    volume_name: Optional[str] = None
    volume_namespace: Optional[str] = None

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            storageos=_ModelStorageOSVolumeSource(
                fs_type=self.fs_type,
                read_only=self.read_only,
                secret_ref=self.secret_ref,
                volume_name=self.volume_name,
                volume_namespace=self.volume_namespace,
            ),
        )


@dataclass(kw_only=True)
class VsphereVirtualDiskVolume(_BaseVolume):
    """`VsphereVirtualDiskVolume` represents a vSphere virtual disk volume to mount."""

    fs_type: Optional[str] = None
    storage_policy_id: Optional[str] = None
    storage_policy_name: Optional[str] = None
    volume_path: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            vsphere_volume=_ModelVsphereVirtualDiskVolumeSource(
                fs_type=self.fs_type,
                storage_policy_id=self.storage_policy_id,
                storage_policy_name=self.storage_policy_name,
                volume_path=self.volume_path,
            ),
        )


@dataclass(kw_only=True)
class ExistingVolume(_BaseVolume):
    """`ExistingVolume` is a representation of an existing volume in K8s.

    The existing volume is mounted based on the supplied claim name. This tells K8s that the specified persistent
    volume claim should be used to mount a volume to a pod.
    """

    claim_name: str

    def _build_volume(self) -> _ModelVolume:
        assert self.name
        return _ModelVolume(
            name=self.name,
            persistent_volume_claim=_ModelPersistentVolumeClaimVolumeSource(
                claim_name=self.claim_name, read_only=self.read_only
            ),
        )


@dataclass(kw_only=True)
class Volume(_BaseVolume):
    """Volume represents a basic, dynamic, volume representation.

    This `Volume` cannot only be instantiated to be used for mounting purposes but also for dynamically privisioning
    volumes in K8s. When the volume is used a corresponding persistent volume claim is also created on workflow
    submission.
    """

    data_source: Optional[TypedLocalObjectReference] = None
    data_source_ref: Optional[TypedObjectReference] = None
    resources: Optional[VolumeResourceRequirements] = None
    selector: Optional[v1.LabelSelector] = None
    storage_class_name: Optional[str] = None
    volume_attributes_class_name: Optional[str] = None
    volume_mode: Optional[str] = None
    volume_name: Optional[str] = None
    size: Optional[str] = None
    metadata: Optional[ObjectMeta] = None
    access_modes: List[str | AccessMode] = field(default_factory=lambda: [AccessMode.read_write_once])

    def __post_init__(self):
        if not self.name:
            self.name = str(uuid.uuid4())

        if not self.access_modes:
            self.access_modes = [AccessMode.read_write_once]
        else:
            result: List[str | AccessMode] = []
            for mode in self.access_modes:
                if isinstance(mode, AccessMode):
                    result.append(mode)
                elif isinstance(mode, str):
                    result.append(AccessMode(mode))

            self.access_modes = result

        if self.size and self.resources:
            if self.resources.requests is not None and "storage" not in self.resources.requests:
                self.resources.requests["storage"] = resource.Quantity(__root__=self.size)
        elif self.resources is None:
            assert self.size, "at least one of `size` or `resources` must be specified"
            validate_storage_units(self.size)
            self.resources = VolumeResourceRequirements(requests={"storage": resource.Quantity(__root__=self.size)})
        else:  # self.resources is not None
            assert self.resources.requests is not None, "Resource requests are required"
            storage = self.resources.requests.get("storage")
            assert storage is not None, "At least one of `size` or `resources.requests.storage` must be specified"
            validate_storage_units(cast(str, storage))

    def _build_persistent_volume_claim(self) -> _ModelPersistentVolumeClaim:
        return _ModelPersistentVolumeClaim(
            metadata=self.metadata or ObjectMeta(name=self.name),
            spec=_ModelPersistentVolumeClaimSpec(
                access_modes=[str(cast(AccessMode, am).value) for am in self.access_modes]
                if self.access_modes is not None
                else None,
                data_source=self.data_source,
                data_source_ref=self.data_source_ref,
                resources=self.resources,
                selector=self.selector,
                storage_class_name=self.storage_class_name,
                volume_mode=self.volume_mode,
                volume_name=self.volume_name,
            ),
        )

    def _build_volume(self) -> _ModelVolume:
        claim = self._build_persistent_volume_claim()
        assert claim.metadata is not None, "claim metadata is required"
        assert self.name
        return _ModelVolume(
            name=self.name,
            persistent_volume_claim=_ModelPersistentVolumeClaimVolumeSource(
                claim_name=cast(str, claim.metadata.name),
                read_only=self.read_only,
            ),
        )


__all__ = [
    "AccessMode",
    *[c.__name__ for c in _BaseVolume.__subclasses__()],
]
