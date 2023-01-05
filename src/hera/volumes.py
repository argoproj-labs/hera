import uuid
from enum import Enum
from typing import List, Optional, cast

from pydantic import root_validator, validator

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
from hera.models import GitRepoVolumeSource as ModelGitRepoVolumeSource
from hera.models import GlusterfsVolumeSource as ModelGlusterfsVolumeSource
from hera.models import HostPathVolumeSource as ModelHostPathVolumeSource
from hera.models import ISCSIVolumeSource as ModelISCSIVolumeSource
from hera.models import NFSVolumeSource as ModelNFSVolumeSource
from hera.models import ObjectMeta
from hera.models import PersistentVolumeClaim as ModelPersistentVolumeClaim
from hera.models import PersistentVolumeClaimSpec as ModelPersistentVolumeClaimSpec
from hera.models import (
    PersistentVolumeClaimTemplate as ModelPersistentVolumeClaimTemplate,
)
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
from hera.models import Volume as ModelVolume
from hera.models import VolumeMount as ModelVolumeMount
from hera.models import (
    VsphereVirtualDiskVolumeSource as ModelVsphereVirtualDiskVolumeSource,
)
from hera.validators import validate_storage_units


class AccessModeVolume(Enum):
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


class _BaseVolume(ModelVolumeMount):
    name: Optional[str]

    @validator("name", pre=True)
    def _check_name(cls, v):
        if v is None:
            return str(uuid.uuid4())
        return v

    def claim(self) -> ModelPersistentVolumeClaim:
        raise NotImplementedError

    def volume(self) -> ModelVolume:
        raise NotImplementedError

    def mount(self) -> ModelVolumeMount:
        return ModelVolumeMount(
            name=self.name,
            mount_path=self.mount_path,
            mount_propagation=self.mount_propagation,
            read_only=self.read_only,
            sub_path=self.sub_path,
            sub_path_expr=self.sub_path_expr,
        )


class AWSElasticBlockStoreVolumeVolume(_BaseVolume, ModelAWSElasticBlockStoreVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, aws_elastic_block_store=self)


class AzureDiskVolumeVolume(_BaseVolume, ModelAzureDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, azure_disk=self)


class AzureFileVolumeVolume(_BaseVolume, ModelAzureFileVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, azure_file=self)


class CephFSVolumeVolume(_BaseVolume, ModelCephFSVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, cephfs=self)


class CinderVolume(_BaseVolume, ModelCinderVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, cinder=self)


class ConfigMapVolume(_BaseVolume, ModelConfigMapVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, config_map=self)


class CSIVolume(_BaseVolume, ModelCSIVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, csi=self)


class DownwardAPIVolume(_BaseVolume, ModelDownwardAPIVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, downward_api=self)


class EmptyDirVolume(_BaseVolume, ModelEmptyDirVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, empty_dir=self)


class EphemeralVolume(_BaseVolume, ModelEphemeralVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, ephemeral=self)


class FCVolume(_BaseVolume, ModelFCVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, fc=self)


class FlexVolume(_BaseVolume, ModelFlexVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, flex_volume=self)


class FlockerVolume(_BaseVolume, ModelFlockerVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, flocker=self)


class GCEPersistentDiskVolume(_BaseVolume, ModelGCEPersistentDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, gce_persistent_disk=self)


class GitRepoVolume(_BaseVolume, ModelGitRepoVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, git_repo=self)


class GlusterfsVolume(_BaseVolume, ModelGlusterfsVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, glusterfs=self)


class HostPathVolume(_BaseVolume, ModelHostPathVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, host_path=self)


class ISCSIVolume(_BaseVolume, ModelISCSIVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, iscsi=self)


class NFSVolume(_BaseVolume, ModelNFSVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, nfs=self)


class PhotonPersistentDiskVolume(_BaseVolume, ModelPhotonPersistentDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, photon_persistent_disk=self)


class PortworxVolume(_BaseVolume, ModelPortworxVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, portworx_volume=self)


class ProjectedVolume(_BaseVolume, ModelProjectedVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, projected=self)


class QuobyteVolume(_BaseVolume, ModelQuobyteVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, quobyte=self)


class RBDVolume(_BaseVolume, ModelRBDVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, rbd=self)


class ScaleIOVolume(_BaseVolume, ModelScaleIOVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, scale_io=self)


class SecretVolume(_BaseVolume, ModelSecretVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, secret=self)


class StorageOSVolume(_BaseVolume, ModelStorageOSVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, storageos=self)


class VsphereVirtualDiskVolume(_BaseVolume, ModelVsphereVirtualDiskVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, vsphere_volume=self)


class ExistingVolume(_BaseVolume, ModelPersistentVolumeClaimVolumeSource):
    def volume(self) -> ModelVolume:
        return ModelVolume(name=self.name, persistent_volume_claim=self)


class VolumeVolume(_BaseVolume, ModelPersistentVolumeClaimSpec):
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

    def claim(self) -> ModelPersistentVolumeClaimTemplate:
        return ModelPersistentVolumeClaimTemplate(
            metadata=self.metadata,
            spec=ModelPersistentVolumeClaimSpec(
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

    def volume(self) -> ModelVolume:
        claim = self.claim()
        return ModelVolume(
            name=self.name,
            persistent_volume_claim=ModelPersistentVolumeClaimVolumeSource(
                claim_name=claim.metadata.name,
                read_only=self.read_only,
            ),
        )
