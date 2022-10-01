import pytest

from hera.volumes import AccessMode, EmptyDirVolume, Volume, _BaseVolume


class TestAccessMode:
    def test_str_returns_expected_value(self):
        assert str(AccessMode.ReadWriteOnce) == "ReadWriteOnce"
        assert str(AccessMode.ReadOnlyMany) == "ReadOnlyMany"
        assert str(AccessMode.ReadWriteMany) == "ReadWriteMany"
        assert str(AccessMode.ReadWriteOncePod) == "ReadWriteOncePod"
        assert len(AccessMode) == 4


class TestBaseVolume:

    def test_build_claim_spec_returns_None(self):
        assert _BaseVolume('/mnt')._build_claim_spec() is None


def test_empty_dir_volume_created_without_size():
    edv = EmptyDirVolume()._build_claim_spec()
    assert edv.name is not None
    assert edv.empty_dir.medium == "Memory"
    assert not hasattr(edv.empty_dir, "size_limit")


def test_empty_dir_volume_created_with_size():
    edv = EmptyDirVolume(size="5Gi")._build_claim_spec()
    assert edv.name is not None
    assert edv.empty_dir.medium == "Memory"
    assert edv.empty_dir.size_limit == "5Gi"


def test_volume_created_with_defaults():
    v = Volume(name="v", size="1Gi", mount_path="/test")
    spec = v._build_claim_spec().spec

    assert len(spec.access_modes) == 1
    assert spec.access_modes == ["ReadWriteOnce"]
    assert spec.resources.requests["storage"] == "1Gi"
    assert spec.storage_class_name == "standard"


def test_volume_created_with_multiple_access_modes():
    v = Volume(
        name="v", size="1Gi", mount_path="/test", access_modes=[AccessMode.ReadWriteOnce, AccessMode.ReadWriteOncePod]
    )
    spec = v._build_claim_spec().spec

    assert len(spec.access_modes) == 2
    assert spec.access_modes == ["ReadWriteOnce", "ReadWriteOncePod"]
    assert spec.resources.requests["storage"] == "1Gi"
    assert spec.storage_class_name == "standard"


def test_volume_fails_creation_with_string_access_modes():
    with pytest.raises(AssertionError):
        Volume(name="v", size="1Gi", mount_path="/test", access_modes=["ReadWriteTwice"])


def test_volume_mount():
    v = Volume(name="v", size="1Gi", mount_path="/test", sub_path="test.txt")
    mount = v._build_mount()

    assert mount["mount_path"] == "/test"
    assert mount["name"] == "v"
    assert mount["sub_path"] == "test.txt"
