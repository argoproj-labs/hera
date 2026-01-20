"""Tests for third-party volume classes, including deprecated aliases."""

from hera.workflows.models import (
    AWSElasticBlockStoreVolumeSource,
    AzureDiskVolumeSource,
    AzureFileVolumeSource,
    CephFSVolumeSource,
    Volume as ModelVolume,
)
from hera.workflows.volume import (
    AWSElasticBlockStoreVolume,
    AzureDiskVolume,
    AzureFileVolume,
    CephFSVolume,
)


class TestThirdPartyVolumes:
    """Tests for third-party volume classes."""

    def test_aws_elastic_block_store_volume(self):
        new_volume = AWSElasticBlockStoreVolume(
            name="aws-ebs-new",
            mount_path="/mnt/aws-ebs",
            volume_id="vol-123456",
            fs_type="ext4",
        )
        assert new_volume.name == "aws-ebs-new"
        assert new_volume.mount_path == "/mnt/aws-ebs"
        assert new_volume.volume_id == "vol-123456"
        assert new_volume.fs_type == "ext4"

        built_volume = new_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "aws-ebs-new"
        assert isinstance(built_volume.aws_elastic_block_store, AWSElasticBlockStoreVolumeSource)
        assert built_volume.aws_elastic_block_store.volume_id == "vol-123456"
        assert built_volume.aws_elastic_block_store.fs_type == "ext4"

    def test_azure_disk_volume(self):
        new_volume = AzureDiskVolume(
            name="azure-disk-new",
            mount_path="/mnt/azure-disk",
            disk_name="disk-123",
            disk_uri="https://example.com/disk-123",
        )
        assert new_volume.name == "azure-disk-new"
        assert new_volume.mount_path == "/mnt/azure-disk"
        assert new_volume.disk_name == "disk-123"
        assert new_volume.disk_uri == "https://example.com/disk-123"

        built_volume = new_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "azure-disk-new"
        assert isinstance(built_volume.azure_disk, AzureDiskVolumeSource)
        assert built_volume.azure_disk.disk_name == "disk-123"
        assert built_volume.azure_disk.disk_uri == "https://example.com/disk-123"

    def test_azure_file_volume(self):
        new_volume = AzureFileVolume(
            name="azure-file-new",
            mount_path="/mnt/azure-file",
            share_name="share-123",
            secret_name="secret-123",
        )
        assert new_volume.name == "azure-file-new"
        assert new_volume.mount_path == "/mnt/azure-file"
        assert new_volume.share_name == "share-123"
        assert new_volume.secret_name == "secret-123"

        built_volume = new_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "azure-file-new"
        assert isinstance(built_volume.azure_file, AzureFileVolumeSource)
        assert built_volume.azure_file.share_name == "share-123"
        assert built_volume.azure_file.secret_name == "secret-123"

    def test_cephfs_volume(self):
        new_volume = CephFSVolume(
            name="cephfs-new",
            mount_path="/mnt/cephfs",
            monitors=["monitor1", "monitor2"],
            user="user1",
        )
        assert new_volume.name == "cephfs-new"
        assert new_volume.mount_path == "/mnt/cephfs"
        assert new_volume.monitors == ["monitor1", "monitor2"]
        assert new_volume.user == "user1"

        built_volume = new_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "cephfs-new"
        assert isinstance(built_volume.cephfs, CephFSVolumeSource)
        assert built_volume.cephfs.monitors == ["monitor1", "monitor2"]
        assert built_volume.cephfs.user == "user1"
