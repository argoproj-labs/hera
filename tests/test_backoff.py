from argo_workflows.models import IoArgoprojWorkflowV1alpha1Backoff

from hera.backoff import Backoff


class TestBackoff:
    def test_converts_int_to_string_post_init(self):
        bo = Backoff(factor=42)
        assert bo.factor is not None
        assert isinstance(bo.factor, str)
        assert bo.factor == "42"

    def test_build_returns_expected_backoff(self):
        bo = Backoff()
        fields = ["duration", "factor", "max_duration"]
        assert set(list(vars(bo).keys())) == set(fields)
        for field in fields:
            bo = Backoff(**{field: "abc"}).build()
            assert isinstance(bo, IoArgoprojWorkflowV1alpha1Backoff)
            assert hasattr(bo, field)
            assert bo.get(field) == "abc"
            for other_field in fields:
                if other_field == field:
                    continue
                assert not hasattr(bo, other_field)
