import pytest
from pydantic import ValidationError

from hera.volumes import AccessMode, Volume


def test_volume_created_with_defaults():
    v = Volume(name='v', size='1Gi', mount_path='/test')
    spec = v.get_claim_spec().spec

    assert len(spec.access_modes) == 1
    assert spec.access_modes == ['ReadWriteOnce']
    assert spec.resources.requests['storage'] == '1Gi'
    assert spec.storage_class_name == 'standard'


def test_volume_created_with_multiple_access_modes():
    v = Volume(
        name='v', size='1Gi', mount_path='/test', access_modes=[AccessMode.ReadWriteOnce, AccessMode.ReadWriteOncePod]
    )
    spec = v.get_claim_spec().spec

    assert len(spec.access_modes) == 2
    assert spec.access_modes == ['ReadWriteOnce', 'ReadWriteOncePod']
    assert spec.resources.requests['storage'] == '1Gi'
    assert spec.storage_class_name == 'standard'


def test_volume_fails_creation_with_string_access_modes():
    with pytest.raises(ValidationError) as e:
        Volume(name='v', size='1Gi', mount_path='/test', access_modes=['ReadWriteTwice'])
