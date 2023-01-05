import uuid
from enum import Enum
from typing import List, Optional, TypeVar, cast

from pydantic import root_validator, validator

from hera._base_model import BaseModel
from hera.models import (
    AWSElasticBlockStoreVolumeSource as ModelAWSElasticBlockStoreVolumeSource,
)
from hera.models import AzureDiskVolumeSource as ModelAzureDiskVolumeSource
from hera.models import AzureFileVolumeSource as ModelAzureFileVolumeSource
from hera.models import CephFSVolumeSource as ModelCephFSVolumeSource
from hera.models import CinderVolumeSource as ModelCinderVolumeSource
from hera.models import ConfigMapVolumeSource as ModelConfigMapVolumeSource
from hera.models import CSIVolumeSource as ModelCSIVolumeSource
from hera.models import DownwardAPIVolumeSource as ModelDownwardAPIVolumeSource
from hera.models import EmptyDirVolumeSource as ModelEmptyDirVolumeSource
from hera.models import EphemeralVolumeSource as ModelEphemeralVolumeSource
from hera.models import FCVolumeSource as ModelFCVolumeSource
from hera.models import FlexVolumeSource as ModelFlexVolumeSource
from hera.models import FlockerVolumeSource as ModelFlockerVolumeSource
from hera.models import (
    GCEPersistentDiskVolumeSource as ModelGCEPersistentDiskVolumeSource,
)
from hera.models import Volume as ModelVolume
from hera.models import GitRepoVolumeSource as ModelGitRepoVolumeSource
from hera.models import GlusterfsVolumeSource as ModelGlusterfsVolumeSource
from hera.models import HostPathVolumeSource as ModelHostPathVolumeSource
from hera.models import ISCSIVolumeSource as ModelISCSIVolumeSource
from hera.models import LabelSelector
from hera.models import NFSVolumeSource as ModelNFSVolumeSource
from hera.models import ObjectMeta
from hera.models import PersistentVolumeClaim as ModelPersistentVolumeClaim
from hera.models import PersistentVolumeClaimSpec as ModelPersistentVolumeClaimSpec
from hera.models import PersistentVolumeClaimStatus
from hera.models import (
    PersistentVolumeClaimVolumeSource as ModelPersistentVolumeClaimVolumeSource,
)
from hera.models import (
    PhotonPersistentDiskVolumeSource as ModelPhotonPersistentDiskVolumeSource,
)
from hera.models import PortworxVolumeSource as ModelPortworxVolumeSource
from hera.models import ProjectedVolumeSource as ModelProjectedVolumeSource
from hera.models import QuobyteVolumeSource as ModelQuobyteVolumeSource
from hera.models import RBDVolumeSource as ModelRBDVolumeSource
from hera.models import ResourceRequirements
from hera.models import ScaleIOVolumeSource as ModelScaleIOVolumeSource
from hera.models import SecretVolumeSource as ModelSecretVolumeSource
from hera.models import StorageOSVolumeSource as ModelStorageOSVolumeSource
from hera.models import TypedLocalObjectReference
from hera.models import (
    VsphereVirtualDiskVolumeSource as ModelVsphereVirtualDiskVolumeSource,
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


VolumeType = TypeVar("VolumeType", bound="_BaseVolume")


class _BaseVolume(BaseModel):
    name: Optional[str]

    @validator("name", pre=True)
    def _check_name(cls, v):
        if v is None:
            return str(uuid.uuid4())
        return v

    def claim(self)->ModelPersistentVolumeClaim:
        raise NotImplementedError

    def volume(self) ->ModelVolume:
        raise NotImplementedError


class AWSElasticBlockStore(_BaseVolume, ModelAWSElasticBlockStoreVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, aws_elastic_block_store=self)


class AzureDisk(_BaseVolume, ModelAzureDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, azure_disk=self)


class AzureFile(_BaseVolume, ModelAzureFileVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, azure_file=self)


class CephFS(_BaseVolume, ModelCephFSVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, cephfs=self)


class Cinder(_BaseVolume, ModelCinderVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, cinder=self)


class ConfigMap(_BaseVolume, ModelConfigMapVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, config_map=self)


class CSI(_BaseVolume, ModelCSIVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, csi=self)


class DownwardAPI(_BaseVolume, ModelDownwardAPIVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, downward_api=self)


class EmptyDir(_BaseVolume, ModelEmptyDirVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, empty_dir=self)


class Ephemeral(_BaseVolume, ModelEphemeralVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, ephemeral=self)


class FC(_BaseVolume, ModelFCVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, fc=self)


class Flex(_BaseVolume, ModelFlexVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, flex_volume=self)


class Flocker(_BaseVolume, ModelFlockerVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, flocker=self)


class GCEPersistentDisk(_BaseVolume, ModelGCEPersistentDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, gce_persistent_disk=self)


class GitRepo(_BaseVolume, ModelGitRepoVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, git_repo=self)


class Glusterfs(_BaseVolume, ModelGlusterfsVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, glusterfs=self)


class HostPath(_BaseVolume, ModelHostPathVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, host_path=self)


class ISCSI(_BaseVolume, ModelISCSIVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, iscsi=self)


class NFS(_BaseVolume, ModelNFSVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, nfs=self)


class PhotonPersistentDisk(_BaseVolume, ModelPhotonPersistentDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, photon_persistent_disk=self)


class Portworx(_BaseVolume, ModelPortworxVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, portworx_volume=self)


class Projected(_BaseVolume, ModelProjectedVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, projected=self)


class Quobyte(_BaseVolume, ModelQuobyteVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, quobyte=self)


class RBD(_BaseVolume, ModelRBDVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, rbd=self)


class ScaleIO(_BaseVolume, ModelScaleIOVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, scale_io=self)


class Secret(_BaseVolume, ModelSecretVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, secret=self)


class StorageOS(_BaseVolume, ModelStorageOSVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, storageos=self)


class VsphereVirtualDisk(_BaseVolume, ModelVsphereVirtualDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, vsphere_volume=self)


class Existing(_BaseVolume, ModelPersistentVolumeClaimVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, persistent_volume_claim=self)


class Volume(_BaseVolume, ModelPersistentVolumeClaimSpec):
    api_version: Optional[str] = None
    kind: Optional[str]
    size: Optional[str] = None
    name: Optional[str] = None
    resources: Optional[ResourceRequirements] = None
    metadata: Optional[ObjectMeta] = None
    access_modes: Optional[List[str]] = None
    data_source: Optional[TypedLocalObjectReference] = None
    data_source_ref: Optional[TypedLocalObjectReference] = None
    selector: Optional[LabelSelector] = None
    storage_class_name: Optional[str] = "standard"
    volume_mode: Optional[str] = None
    volume_name: Optional[str] = None
    status: Optional[PersistentVolumeClaimStatus] = None

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

    def claim(self) -> ModelPersistentVolumeClaim:
        return ModelPersistentVolumeClaim(
            api_version=self.api_version,
            kind=self.kind,
            metadata=self.metadata,
            spec=ModelPersistentVolumeClaimSpec(
                access_modes=self.access_modes,
                data_source=self.data_source,
                data_source_ref=self.data_source_ref,
                resources=self.resources,
                selector=self.selector,
                storage_class_name=self.storage_class_name,
                volume_mode=self.volume_mode,
                volume_name=self.volume_name,
            ),
            status=self.status,
        )
