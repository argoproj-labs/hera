from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1ArchiveStrategy,
    IoArgoprojWorkflowV1alpha1TarStrategy,
)

from hera.archive import Archive


class TestArchive:
    def test_build_sets_expected_fields(self):
        archive = Archive(disable_compression=True).build()
        assert isinstance(archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(archive, "_none")
        assert archive._none
        assert not hasattr(archive, "tar")
        assert not hasattr(archive, "zip")

        archive = Archive(tar_compression_level=1).build()
        assert isinstance(archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(archive, "tar")
        assert isinstance(archive.tar, IoArgoprojWorkflowV1alpha1TarStrategy)
        assert hasattr(archive.tar, "compression_level")
        assert archive.tar.compression_level == 1
        assert not hasattr(archive, "_none")
        assert not hasattr(archive, "zip")

        archive = Archive(zip=True).build()
        assert isinstance(archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(archive, "zip")
        assert archive.zip
        assert not hasattr(archive, "_none")
        assert not hasattr(archive, "tar")
