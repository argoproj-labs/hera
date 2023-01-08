import uuid
from enum import Enum
from typing import List, Optional, cast

from pydantic import root_validator, validator

from hera.models import (
    AWSElasticBlockStoreVolumeSource as _ModelAWSElasticBlockStoreVolumeSource,
)
from hera.models import AzureDiskVolumeSource as _ModelAzureDiskVolumeSource
from hera.models import AzureFileVolumeSource as _ModelAzureFileVolumeSource
from hera.models import CephFSVolumeSource as _ModelCephFSVolumeSource
from hera.models import CinderVolumeSource as _ModelCinderVolumeSource
from hera.models import ConfigMapVolumeSource as _ModelConfigMapVolumeSource
from hera.models import CSIVolumeSource as _ModelCSIVolumeSource
from hera.models import DownwardAPIVolumeSource as _ModelDownwardAPIVolumeSource
from hera.models import EmptyDirVolumeSource as _ModelEmptyDirVolumeSource
from hera.models import EphemeralVolumeSource as _ModelEphemeralVolumeSource
from hera.models import FCVolumeSource as _ModelFCVolumeSource
from hera.models import FlexVolumeSource as _ModelFlexVolumeSource
from hera.models import FlockerVolumeSource as _ModelFlockerVolumeSource
from hera.models import (
    GCEPersistentDiskVolumeSource as _ModelGCEPersistentDiskVolumeSource,
)
from hera.models import GitRepoVolumeSource as _ModelGitRepoVolumeSource
from hera.models import GlusterfsVolumeSource as _ModelGlusterfsVolumeSource
from hera.models import HostPathVolumeSource as _ModelHostPathVolumeSource
from hera.models import ISCSIVolumeSource as _ModelISCSIVolumeSource
from hera.models import NFSVolumeSource as _ModelNFSVolumeSource
from hera.models import ObjectMeta
from hera.models import PersistentVolumeClaim as _ModelPersistentVolumeClaim
from hera.models import PersistentVolumeClaimSpec as _ModelPersistentVolumeClaimSpec
from hera.models import (
    PersistentVolumeClaimTemplate as _ModelPersistentVolumeClaimTemplate,
)
from hera.models import (
    PersistentVolumeClaimVolumeSource as _ModelPersistentVolumeClaimVolumeSource,
)
from hera.models import (
    PhotonPersistentDiskVolumeSource as _ModelPhotonPersistentDiskVolumeSource,
)
from hera.models import PortworxVolumeSource as _ModelPortworxVolumeSource
from hera.models import ProjectedVolumeSource as _ModelProjectedVolumeSource
from hera.models import QuobyteVolumeSource as _ModelQuobyteVolumeSource
from hera.models import RBDVolumeSource as _ModelRBDVolumeSource
from hera.models import ResourceRequirements
from hera.models import ScaleIOVolumeSource as _ModelScaleIOVolumeSource
from hera.models import SecretVolumeSource as _ModelSecretVolumeSource
from hera.models import StorageOSVolumeSource as _ModelStorageOSVolumeSource
from hera.models import Volume as _ModelVolume
from hera.models import VolumeMount as _ModelVolumeMount
from hera.models import (
    VsphereVirtualDiskVolumeSource as _ModelVsphereVirtualDiskVolumeSource,
)
from hera.validators import validate_storage_units


class AccessMode(Enum):
    """A representations of the volume access modes for Kubernetes.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes for more information.
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

    def __str__(self):
        return str(self.value)


class _BaseVolume(_ModelVolumeMount):
    name: Optional[str]

    @validator("name", pre=True)
    def _check_name(cls, v):
        if v is None:
            return str(uuid.uuid4())
        return v

    def claim(self) -> _ModelPersistentVolumeClaimTemplate:
        raise NotImplementedError

    def volume(self) -> _ModelVolume:
        raise NotImplementedError

    def mount(self) -> _ModelVolumeMount:
        return _ModelVolumeMount(
            name=self.name,
            mount_path=self.mount_path,
            mount_propagation=self.mount_propagation,
            read_only=self.read_only,
            sub_path=self.sub_path,
            sub_path_expr=self.sub_path_expr,
        )


class AWSElasticBlockStoreVolumeVolume(_BaseVolume, _ModelAWSElasticBlockStoreVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, aws_elastic_block_store=self)


class AzureDiskVolumeVolume(_BaseVolume, _ModelAzureDiskVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, azure_disk=self)


class AzureFileVolumeVolume(_BaseVolume, _ModelAzureFileVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, azure_file=self)


class CephFSVolumeVolume(_BaseVolume, _ModelCephFSVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, cephfs=self)


class CinderVolume(_BaseVolume, _ModelCinderVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, cinder=self)


class ConfigMapVolume(_BaseVolume, _ModelConfigMapVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, config_map=self)


class CSIVolume(_BaseVolume, _ModelCSIVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, csi=self)


class DownwardAPIVolume(_BaseVolume, _ModelDownwardAPIVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, downward_api=self)


class EmptyDirVolume(_BaseVolume, _ModelEmptyDirVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, empty_dir=self)


class EphemeralVolume(_BaseVolume, _ModelEphemeralVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, ephemeral=self)


class FCVolume(_BaseVolume, _ModelFCVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, fc=self)


class FlexVolume(_BaseVolume, _ModelFlexVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, flex_volume=self)


class FlockerVolume(_BaseVolume, _ModelFlockerVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, flocker=self)


class GCEPersistentDiskVolume(_BaseVolume, _ModelGCEPersistentDiskVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, gce_persistent_disk=self)


class GitRepoVolume(_BaseVolume, _ModelGitRepoVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, git_repo=self)


class GlusterfsVolume(_BaseVolume, _ModelGlusterfsVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, glusterfs=self)


class HostPathVolume(_BaseVolume, _ModelHostPathVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, host_path=self)


class ISCSIVolume(_BaseVolume, _ModelISCSIVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, iscsi=self)


class NFSVolume(_BaseVolume, _ModelNFSVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, nfs=self)


class PhotonPersistentDiskVolume(_BaseVolume, _ModelPhotonPersistentDiskVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, photon_persistent_disk=self)


class PortworxVolume(_BaseVolume, _ModelPortworxVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, portworx_volume=self)


class ProjectedVolume(_BaseVolume, _ModelProjectedVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, projected=self)


class QuobyteVolume(_BaseVolume, _ModelQuobyteVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, quobyte=self)


class RBDVolume(_BaseVolume, _ModelRBDVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, rbd=self)


class ScaleIOVolume(_BaseVolume, _ModelScaleIOVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, scale_io=self)


class SecretVolume(_BaseVolume, _ModelSecretVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, secret=self)


class StorageOSVolume(_BaseVolume, _ModelStorageOSVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, storageos=self)


class VsphereVirtualDiskVolume(_BaseVolume, _ModelVsphereVirtualDiskVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, vsphere_volume=self)


class ExistingVolume(_BaseVolume, _ModelPersistentVolumeClaimVolumeSource):
    def volume(self) -> _ModelVolume:
        return _ModelVolume(name=self.name, persistent_volume_claim=self)


class Volume(_BaseVolume, _ModelPersistentVolumeClaimSpec):
    size: Optional[str] = None
    name: Optional[str] = None
    resources: Optional[ResourceRequirements] = None
    metadata: Optional[ObjectMeta] = None
    access_modes: Optional[List[AccessMode]] = None
    storage_class_name: Optional[str] = "standard"

    @root_validator(pre=True)
    def _merge_reqs(cls, values):
        if "size" in values and "resources" in values:
            resources: ResourceRequirements = values.get("resources")
            if "storage" in resources.requests:
                pass  # take the storage specification in resources
            else:
                resources.requests["storage"] = values.get("size")
        elif "resources" not in values:
            assert "size" in values, "at least one of `size` or `resources` must be specified"
            validate_storage_units(values.get("size"))
            values["resources"] = ResourceRequirements(requests={"storage": values.get("size")})
        elif "resources" in values:
            resources: ResourceRequirements = values.get("resources")
            storage = resources.requests.get("storage")
            assert storage is not None, "at least one of `size` or `resources.requests.storage` must be specified"
            storage = cast(str, storage)
            validate_storage_units(storage)
        return values

    def claim(self) -> _ModelPersistentVolumeClaimTemplate:
        return _ModelPersistentVolumeClaimTemplate(
            metadata=self.metadata,
            spec=_ModelPersistentVolumeClaimSpec(
                access_modes=[str(am.value) for am in self.access_modes],
                data_source=self.data_source,
                data_source_ref=self.data_source_ref,
                resources=self.resources,
                selector=self.selector,
                storage_class_name=self.storage_class_name,
                volume_mode=self.volume_mode,
                volume_name=self.volume_name,
            ),
        )

    def volume(self) -> _ModelVolume:
        claim = self.claim()
        return _ModelVolume(
            name=self.name,
            persistent_volume_claim=_ModelPersistentVolumeClaimVolumeSource(
                claim_name=claim.metadata.name,
                read_only=self.read_only,
            ),
        )


__all__ = [
    "AccessMode",
    *[c.__class__.__name__ for c in _BaseVolume.__subclasses__()],
]
