from hera import VolumeClaimGCStrategy


class TestVolumeClaimGCStrategy:
    def test_str_returns_expected_value(self):
        assert str(VolumeClaimGCStrategy.OnWorkflowSuccess) == "OnWorkflowSuccess"
        assert str(VolumeClaimGCStrategy.OnWorkflowCompletion) == "OnWorkflowCompletion"
        assert len(VolumeClaimGCStrategy) == 2
