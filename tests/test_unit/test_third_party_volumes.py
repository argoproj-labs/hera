"""Tests for third-party volume classes, including deprecated aliases."""

import pytest

from hera.workflows.models import (
    AWSElasticBlockStoreVolumeSource,
    AzureDiskVolumeSource,
    AzureFileVolumeSource,
    CephFSVolumeSource,
    Volume as ModelVolume,
)
from hera.workflows.volume import (
    AWSElasticBlockStoreVolume,
    AWSElasticBlockStoreVolumeVolume,
    AzureDiskVolume,
    AzureDiskVolumeVolume,
    AzureFileVolume,
    AzureFileVolumeVolume,
    CephFSVolume,
    CephFSVolumeVolume,
)


class TestThirdPartyVolumes:
    """Tests for third-party volume classes."""

    def test_deprecation_warnings(self):
        """Test that using deprecated volume classes raises deprecation warnings."""
        with pytest.warns(DeprecationWarning, match="AWSElasticBlockStoreVolumeVolume.*deprecated"):
            AWSElasticBlockStoreVolumeVolume(name="test", mount_path="/test", volume_id="vol-123")

        with pytest.warns(DeprecationWarning, match="AzureDiskVolumeVolume.*deprecated"):
            AzureDiskVolumeVolume(name="test", mount_path="/test", disk_name="disk-123", disk_uri="uri")

        with pytest.warns(DeprecationWarning, match="AzureFileVolumeVolume.*deprecated"):
            AzureFileVolumeVolume(name="test", mount_path="/test", share_name="share", secret_name="secret")

        with pytest.warns(DeprecationWarning, match="CephFSVolumeVolume.*deprecated"):
            CephFSVolumeVolume(name="test", mount_path="/test", monitors=["monitor1"])

    def test_aws_elastic_block_store_volume(self):
        """Test that both old (deprecated) and new AWS EBS volume classes work correctly."""
        # Test new class
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

        # Test deprecated class
        old_volume = AWSElasticBlockStoreVolumeVolume(
            name="aws-ebs-old",
            mount_path="/mnt/aws-ebs",
            volume_id="vol-123456",
            fs_type="ext4",
        )
        # Verify it's an instance of both the old and new classes
        assert isinstance(old_volume, AWSElasticBlockStoreVolumeVolume)
        assert isinstance(old_volume, AWSElasticBlockStoreVolume)

        # Verify it has the same behavior as the new class
        assert old_volume.name == "aws-ebs-old"
        assert old_volume.mount_path == "/mnt/aws-ebs"
        assert old_volume.volume_id == "vol-123456"
        assert old_volume.fs_type == "ext4"

        built_volume = old_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "aws-ebs-old"
        assert isinstance(built_volume.aws_elastic_block_store, AWSElasticBlockStoreVolumeSource)
        assert built_volume.aws_elastic_block_store.volume_id == "vol-123456"
        assert built_volume.aws_elastic_block_store.fs_type == "ext4"

    def test_azure_disk_volume(self):
        """Test that both old (deprecated) and new Azure Disk volume classes work correctly."""
        # Test new class
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

        # Test deprecated class
        old_volume = AzureDiskVolumeVolume(
            name="azure-disk-old",
            mount_path="/mnt/azure-disk",
            disk_name="disk-123",
            disk_uri="https://example.com/disk-123",
        )
        # Verify it's an instance of both the old and new classes
        assert isinstance(old_volume, AzureDiskVolumeVolume)
        assert isinstance(old_volume, AzureDiskVolume)

        # Verify it has the same behavior as the new class
        assert old_volume.name == "azure-disk-old"
        assert old_volume.mount_path == "/mnt/azure-disk"
        assert old_volume.disk_name == "disk-123"
        assert old_volume.disk_uri == "https://example.com/disk-123"

        built_volume = old_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "azure-disk-old"
        assert isinstance(built_volume.azure_disk, AzureDiskVolumeSource)
        assert built_volume.azure_disk.disk_name == "disk-123"
        assert built_volume.azure_disk.disk_uri == "https://example.com/disk-123"

    def test_azure_file_volume(self):
        """Test that both old (deprecated) and new Azure File volume classes work correctly."""
        # Test new class
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

        # Test deprecated class
        old_volume = AzureFileVolumeVolume(
            name="azure-file-old",
            mount_path="/mnt/azure-file",
            share_name="share-123",
            secret_name="secret-123",
        )
        # Verify it's an instance of both the old and new classes
        assert isinstance(old_volume, AzureFileVolumeVolume)
        assert isinstance(old_volume, AzureFileVolume)

        # Verify it has the same behavior as the new class
        assert old_volume.name == "azure-file-old"
        assert old_volume.mount_path == "/mnt/azure-file"
        assert old_volume.share_name == "share-123"
        assert old_volume.secret_name == "secret-123"

        built_volume = old_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "azure-file-old"
        assert isinstance(built_volume.azure_file, AzureFileVolumeSource)
        assert built_volume.azure_file.share_name == "share-123"
        assert built_volume.azure_file.secret_name == "secret-123"

    def test_cephfs_volume(self):
        """Test that both old (deprecated) and new CephFS volume classes work correctly."""
        # Test new class
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

        # Test deprecated class
        old_volume = CephFSVolumeVolume(
            name="cephfs-old",
            mount_path="/mnt/cephfs",
            monitors=["monitor1", "monitor2"],
            user="user1",
        )
        # Verify it's an instance of both the old and new classes
        assert isinstance(old_volume, CephFSVolumeVolume)
        assert isinstance(old_volume, CephFSVolume)

        # Verify it has the same behavior as the new class
        assert old_volume.name == "cephfs-old"
        assert old_volume.mount_path == "/mnt/cephfs"
        assert old_volume.monitors == ["monitor1", "monitor2"]
        assert old_volume.user == "user1"

        built_volume = old_volume._build_volume()
        assert isinstance(built_volume, ModelVolume)
        assert built_volume.name == "cephfs-old"
        assert isinstance(built_volume.cephfs, CephFSVolumeSource)
        assert built_volume.cephfs.monitors == ["monitor1", "monitor2"]
        assert built_volume.cephfs.user == "user1"
