import pytest

from hera import Resources


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


def test_init_passes():
    r = Resources(
        cpu_request=1,
        cpu_limit=2,
        memory_request="2Gi",
        memory_limit="3Gi",
        gpus=1,
    )
    assert r.cpu_request == 1
    assert r.cpu_limit == 2
    assert r.memory_request == "2Gi"
    assert r.memory_limit == "3Gi"
    assert r.gpus == 1


def test_max_set_to_min_if_max_not_specified_with_overwrite():
    r = Resources(cpu_limit=1, memory_limit="4Gi")
    assert r.cpu_request == r.cpu_limit == 1
    assert r.memory_request == r.memory_limit == "4Gi"


def test_max_not_set_to_min_if_max_not_specified_with_no_overwrite():
    r = Resources(cpu_request=1, memory_request="4Gi")
    assert r.cpu_request == 1
    assert r.cpu_limit is None
    assert r.memory_request == "4Gi"
    assert r.memory_limit is None
