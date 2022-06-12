from hera.memoize import Memoize


def test_memoize_contains_expected_spec():
    m = Memoize('a', 'b', '1h')
    assert m.key == 'a'
    assert m.config_map_name == 'b'
    assert m.max_age == '1h'

    spec = m.get_spec()
    assert spec.key == '{{inputs.parameters.a}}'
    assert spec.cache.config_map.key == 'b'
    assert spec.max_age == '1h'
