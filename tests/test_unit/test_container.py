import pytest

from hera.workflows._mixins import ContainerMixin
from hera.workflows.models import ImagePullPolicy


class TestContainerMixin:
    def test_image_pull_policy(self):
        with pytest.raises(KeyError):
            ContainerMixin(image_pull_policy="test")._build_image_pull_policy()
        assert ContainerMixin(image_pull_policy=None)._build_image_pull_policy() is None
        assert (
            ContainerMixin(image_pull_policy=ImagePullPolicy.always)._build_image_pull_policy()
            == ImagePullPolicy.always.value
        )
        assert ContainerMixin(image_pull_policy="always")._build_image_pull_policy() == ImagePullPolicy.always.value
        assert ContainerMixin(image_pull_policy="Always")._build_image_pull_policy() == ImagePullPolicy.always.value
