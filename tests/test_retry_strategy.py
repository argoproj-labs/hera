from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Backoff,
    IoArgoprojWorkflowV1alpha1RetryStrategy,
)

from hera.workflows import Backoff, RetryPolicy, RetryStrategy


class TestRetryStrategy:
    def test_post_init_converts_str_to_int(self):
        rs = RetryStrategy(limit=42)
        assert rs.limit is not None
        assert isinstance(rs.limit, str)
        assert rs.limit == "42"

    def test_build_adds_fields_as_expected(self):
        s = RetryStrategy(backoff=Backoff(duration="1m")).build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1RetryStrategy)
        assert hasattr(s, "backoff")
        assert isinstance(s.backoff, IoArgoprojWorkflowV1alpha1Backoff)
        assert hasattr(s.backoff, "duration")
        assert s.backoff.duration == "1m"
        assert not hasattr(s, "expression")
        assert not hasattr(s, "limit")
        assert hasattr(s, "retry_policy")
        assert s.retry_policy == "Always"

        s = RetryStrategy(expression="abc").build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1RetryStrategy)
        assert hasattr(s, "expression")
        assert s.expression == "abc"
        assert not hasattr(s, "backoff")
        assert not hasattr(s, "limit")
        assert hasattr(s, "retry_policy")
        assert s.retry_policy == "Always"

        s = RetryStrategy(limit=42).build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1RetryStrategy)
        assert hasattr(s, "limit")
        assert s.limit == "42"
        assert not hasattr(s, "backoff")
        assert not hasattr(s, "expression")
        assert hasattr(s, "retry_policy")
        assert s.retry_policy == "Always"

        s = RetryStrategy(retry_policy=RetryPolicy.OnTransientError).build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1RetryStrategy)
        assert hasattr(s, "retry_policy")
        assert s.retry_policy == "OnTransientError"
        assert not hasattr(s, "limit")
        assert not hasattr(s, "backoff")
        assert not hasattr(s, "expression")
