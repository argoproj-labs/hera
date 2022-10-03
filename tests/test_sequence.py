import pytest
from argo_workflows.models import IoArgoprojWorkflowV1alpha1Sequence

from hera.sequence import Sequence


class TestSequence:
    def test_post_init_raises(self):
        with pytest.raises(ValueError) as e:
            Sequence("abc", count=1, end=42)
        assert str(e.value) == "Cannot use both `count` and `end`"

    def test_post_init_converts(self):
        s = Sequence("abc", count=42)
        assert s.count is not None
        assert isinstance(s.count, str)
        assert s.start is None
        assert s.end is None
        assert s.format is not None

        s = Sequence("abc", start=1, end=42)
        assert s.count is None
        assert s.start is not None
        assert isinstance(s.start, str)
        assert s.end is not None
        assert isinstance(s.end, str)
        assert s.format is not None

    def test_build(self):
        s = Sequence("abc", count=42).build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1Sequence)
        assert hasattr(s, "count")
        assert not hasattr(s, "start")
        assert not hasattr(s, "end")
        assert s.count == "42"

        s = Sequence("abc", start=1, end=42).build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1Sequence)
        assert not hasattr(s, "count")
        assert hasattr(s, "start")
        assert s.start == "1"
        assert hasattr(s, "end")
        assert s.end == "42"
