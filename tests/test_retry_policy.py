from hera.workflows.retry_policy import RetryPolicy


class TestRetryPolicy:
    def test_str_returns_expected_value(self):
        assert str(RetryPolicy.Always) == "Always"
        assert str(RetryPolicy.OnFailure) == "OnFailure"
        assert str(RetryPolicy.OnError) == "OnError"
        assert str(RetryPolicy.OnTransientError) == "OnTransientError"
        assert len(RetryPolicy) == 4
