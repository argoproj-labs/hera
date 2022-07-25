from hera import Memoize


def test_memoize_contains_expected_spec():
    m = Memoize("a", "b", "b-key", "1h")
    assert m.key == "a"
    assert m.config_map_name == "b"
    assert m.config_map_key == "b-key"
    assert m.max_age == "1h"

    spec = m.build()
    assert spec.key == "{{inputs.parameters.a}}"
    assert spec.cache.config_map.name == "b"
    assert spec.cache.config_map.key == "b-key"
    assert spec.max_age == "1h"
