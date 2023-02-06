import pytest

from hera.resources import Resources, _merge_dicts


def test_merge_dicts_raises_on_key_conflict():
    with pytest.raises(Exception) as e:
        _merge_dicts({"a": 1}, {"a": 2})
    assert str(e.value) == "Conflict at `a`"


def test_merge_dicts_passes_on_same_leaf_value():
    d = _merge_dicts({"a": 1}, {"a": 1})
    assert "a" in d
    assert d["a"] == 1


class TestResources:
    def test_init_raises_on_invalid_mem(self):
        with pytest.raises(ValueError):
            Resources(memory_request="4")
        with pytest.raises(ValueError):
            Resources(memory_limit="4")

    def test_init_raises_on_invalid_eph(self):
        with pytest.raises(AssertionError):
            Resources(ephemeral_request="3m")
        with pytest.raises(AssertionError):
            Resources(ephemeral_limit="2m")

    def test_init_raises_on_invalid_cpu(self):
        with pytest.raises(AssertionError):
            Resources(cpu_limit=-1)
        with pytest.raises(AssertionError):
            Resources(cpu_request=2, cpu_limit=1)

    def test_init_passes(self):
        r = Resources(
            cpu_request=1,
            cpu_limit=2,
            memory_request="2Gi",
            memory_limit="3Gi",
            ephemeral_request="2Mi",
            ephemeral_limit="3Mi",
            gpus=1,
        )
        assert r.cpu_request == 1
        assert r.cpu_limit == 2
        assert r.memory_request == "2Gi"
        assert r.memory_limit == "3Gi"
        assert r.ephemeral_request == "2Mi"
        assert r.ephemeral_limit == "3Mi"
        assert r.gpus == 1

    def test_max_set_to_min_if_max_not_specified_with_overwrite(self):
        r = Resources(cpu_limit=1, memory_limit="4Gi")
        assert r.cpu_request == r.cpu_limit == 1
        assert r.memory_request == r.memory_limit == "4Gi"

    def test_max_not_set_to_min_if_max_not_specified_with_no_overwrite(self):
        r = Resources(cpu_request=1, memory_request="4Gi", ephemeral_request="3Mi")
        assert r.cpu_request == 1
        assert r.cpu_limit is None
        assert r.memory_request == "4Gi"
        assert r.memory_limit is None
        assert r.ephemeral_request == "3Mi"
        assert r.ephemeral_limit is None

    def test_built_resources_contain_expected_fields(self):
        r = Resources(
            cpu_request=1,
            memory_request="4Gi",
            ephemeral_request="3Mi",
            cpu_limit=2,
            memory_limit="8Gi",
            ephemeral_limit="5Mi",
        ).build()
        assert hasattr(r, "limits")
        assert "cpu" in r.limits
        assert "memory" in r.limits
        assert "ephemeral-storage" in r.limits
        assert hasattr(r, "requests")
        assert "cpu" in r.requests
        assert "memory" in r.requests
        assert "ephemeral-storage" in r.requests
