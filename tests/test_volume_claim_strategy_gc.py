from hera import GCStrategy


class TestVolumeClaimGCStrategy:
    def test_str_returns_expected_value(self):
        assert str(GCStrategy.OnWorkflowSuccess) == "OnWorkflowSuccess"
        assert str(GCStrategy.OnWorkflowCompletion) == "OnWorkflowCompletion"
        assert len(GCStrategy) == 2
