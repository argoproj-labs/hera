import pytest

from hera import ExistingVolume, Resources, SecretVolume, Volume


def test_init_raises_on_invalid_mem():
    with pytest.raises(ValueError):
        Resources(memory_request="4")
    with pytest.raises(ValueError):
        Resources(memory_limit="4")


def test_init_raises_on_invalid_cpu():
    with pytest.raises(AssertionError):
        Resources(cpu_limit=-1)
    with pytest.raises(AssertionError):
        Resources(cpu_request=2, cpu_limit=1)


def test_init_volume_error_propagates():
    with pytest.raises(ValueError):
        Resources(volumes=[Volume(size="1", mount_path="/path")])


def test_init_passes():
    r = Resources(
        cpu_request=1,
        cpu_limit=2,
        memory_request="2Gi",
        memory_limit="3Gi",
        gpus=1,
        volumes=[
            Volume(size="10Gi", mount_path="/path"),
            ExistingVolume(name="test", mount_path="/path2"),
            SecretVolume(name="secret", secret_name="secret_name", mount_path="/path3"),
        ],
    )
    assert r.cpu_request == 1
    assert r.cpu_limit == 2
    assert r.memory_request == "2Gi"
    assert r.memory_limit == "3Gi"
    assert r.gpus == 1

    vol = r.volumes[0]
    assert isinstance(vol, Volume)
    assert vol.size == "10Gi"
    assert vol.mount_path == "/path"

    ex_vol = r.volumes[1]
    assert isinstance(ex_vol, ExistingVolume)
    assert ex_vol.name == "test"
    assert ex_vol.mount_path == "/path2"

    sc_vol = r.volumes[2]
    assert isinstance(sc_vol, SecretVolume)
    assert sc_vol.name == "secret"
    assert sc_vol.secret_name == "secret_name"
    assert sc_vol.mount_path == "/path3"


def test_max_set_to_min_if_max_not_specified_with_overwrite():
    r = Resources()
    assert r.cpu_request == r.cpu_limit == 1
    assert r.memory_request == r.memory_limit == "4Gi"
    assert r.overwrite_maxs


def test_max_not_set_to_min_if_max_not_specified_with_no_overwrite():
    r = Resources(overwrite_maxs=False)
    assert r.cpu_request == 1
    assert r.cpu_limit is None
    assert r.memory_request == "4Gi"
    assert r.memory_limit is None
    assert r.overwrite_maxs is False


def test_secret_volume_name_generated_when_not_specified():
    s = SecretVolume(secret_name="sn", mount_path="/path")
    assert s.name is not None and s.name is not ""
