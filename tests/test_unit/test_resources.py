import pytest

from hera.workflows.models import ResourceRequirements
from hera.workflows.resources import Resources


class TestResources:
    @pytest.mark.parametrize(
        "cpu_request, cpu_limit, memory_request, memory_limit, ephemeral_request, ephemeral_limit",
        [
            ("500m", "500m", None, None, None, None),
            ("500m", "1000m", None, None, None, None),
            ("0.5", "0.5", None, None, None, None),
            ("0.5", "1", None, None, None, None),
            (0.5, 0.5, None, None, None, None),
            (0.5, 1.0, None, None, None, None),
            (1, 1, None, None, None, None),
            (1, 2, None, None, None, None),
            (1, 2, "1Gi", "1Gi", None, None),
            (1, 2, "1Gi", "2Gi", None, None),
            (1, 2, "256Mi", "256Mi", None, None),
            (1, 2, "256Mi", "512Mi", "50Gi", None),
            (1, 2, "256Mi", "512Mi", "50Gi", "50Gi"),
            (1, 2, "256Mi", "512Mi", "50Gi", "100Gi"),
        ],
    )
    def test_build_valid(
        self, cpu_request, cpu_limit, memory_request, memory_limit, ephemeral_request, ephemeral_limit
    ) -> None:
        resources = Resources(
            cpu_request=cpu_request,
            cpu_limit=cpu_limit,
            memory_request=memory_request,
            memory_limit=memory_limit,
            ephemeral_request=ephemeral_request,
            ephemeral_limit=ephemeral_limit,
        )
        requirements = resources.build()

        assert isinstance(requirements, ResourceRequirements)

        if cpu_request is not None:
            assert requirements.requests["cpu"].__root__ == str(cpu_request)

        if cpu_limit is not None:
            assert requirements.limits["cpu"].__root__ == str(cpu_limit)

        if memory_request is not None:
            assert requirements.requests["memory"].__root__ == memory_request

        if memory_limit is not None:
            assert requirements.limits["memory"].__root__ == memory_limit

        if ephemeral_request is not None:
            assert requirements.requests["ephemeral-storage"].__root__ == ephemeral_request

        if ephemeral_limit is not None:
            assert requirements.limits["ephemeral-storage"].__root__ == ephemeral_limit

    @pytest.mark.parametrize(
        "cpu_request, cpu_limit, memory_request, memory_limit, ephemeral_request, ephemeral_limit, error_message",
        [
            ("500a", None, None, None, None, None, "Invalid decimal unit"),
            (None, None, "500k", None, None, None, "Invalid binary unit"),
            (-1, 1, None, None, None, None, "must be positive"),
            (-0.5, -0.5, None, None, None, None, "must be positive"),
            (0.5, 0.2, None, None, None, None, "request must be smaller or equal to limit"),
            (3, 2, None, None, None, None, "request must be smaller or equal to limit"),
            ("1", "0.5", None, None, None, None, "request must be smaller or equal to limit"),
            ("1000m", "800m", None, None, None, None, "request must be smaller or equal to limit"),
            ("1", "1", "1Gi", "512Mi", None, None, "request must be smaller or equal to limit"),
            ("1", "1", "1Gi", "1Gi", "100Gi", "50Gi", "request must be smaller or equal to limit"),
        ],
    )
    def test_build_invalid(
        self, cpu_request, cpu_limit, memory_request, memory_limit, ephemeral_request, ephemeral_limit, error_message
    ) -> None:
        with pytest.raises(ValueError, match=error_message):
            _ = Resources(
                cpu_request=cpu_request,
                cpu_limit=cpu_limit,
                memory_request=memory_request,
                memory_limit=memory_limit,
                ephemeral_request=ephemeral_request,
                ephemeral_limit=ephemeral_limit,
            )
