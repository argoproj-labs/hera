import pytest
from pydantic import ValidationError

from hera.resources import Resources
from hera.volumes import ExistingVolume, SecretVolume, Volume


def test_init_raises_on_invalid_mem():
    with pytest.raises(ValidationError):
        Resources(min_mem='4')
    with pytest.raises(ValidationError):
        Resources(max_mem='4')


def test_init_raises_on_invalid_cpu():
    with pytest.raises(ValidationError):
        Resources(max_cpu=-1)
    with pytest.raises(ValidationError):
        Resources(min_cpu=2, max_cpu=1)


def test_init_volume_error_propagates():
    with pytest.raises(ValidationError):
        Resources(volume=Volume(size='1', mount_path='/path'))


def test_init_passes():
    r = Resources(
        min_cpu=1,
        max_cpu=2,
        min_mem='2Gi',
        max_mem='3Gi',
        gpus=1,
        volume=Volume(size='10Gi', mount_path='/path'),
        existing_volume=ExistingVolume(name='test', mount_path='/path2'),
        secret_volume=SecretVolume(name='secret', secret_name='secret_name', mount_path="/path3"),
    )
    assert r.min_cpu == 1
    assert r.max_cpu == 2
    assert r.min_mem == '2Gi'
    assert r.max_mem == '3Gi'
    assert r.gpus == 1
    assert r.volume.size == '10Gi'
    assert r.volume.mount_path == '/path'
    assert r.existing_volume.mount_path == '/path2'
    assert r.secret_volume.mount_path == '/path3'


def test_max_set_to_min_if_max_not_specified_with_overwrite():
    r = Resources()
    assert r.min_cpu == r.max_cpu == 1
    assert r.min_mem == r.max_mem == '4Gi'
    assert r.overwrite_maxs


def test_max_not_set_to_min_if_max_not_specified_with_no_overwrite():
    r = Resources(overwrite_maxs=False)
    assert r.min_cpu == 1
    assert r.max_cpu is None
    assert r.min_mem == '4Gi'
    assert r.max_mem is None
    assert r.overwrite_maxs is False

def test_secret_volume_name_generated_when_not_specified():
    r = Resources(secret_volume=SecretVolume(secret_name="sn", mount_path="/path"))
    assert r.secret_volume.name