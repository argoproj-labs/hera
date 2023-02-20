from hera.workflows.suspend import IoArgoprojWorkflowV1alpha1SuspendTemplate, Suspend


class TestSuspend:
    def test_build(self):
        s = Suspend().build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1SuspendTemplate)
        assert not hasattr(s, "duration")

        s = Suspend(duration="42m").build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1SuspendTemplate)
        assert hasattr(s, "duration")
