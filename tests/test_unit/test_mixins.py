from hera.workflows._mixins import ContainerMixin
from hera.workflows.models import ImagePullPolicy


class TestContainerMixin:
    def test_build_image_pull_policy(self) -> None:
        assert ContainerMixin(image_pull_policy="Always")._build_image_pull_policy() == ImagePullPolicy.always
        assert (
            ContainerMixin(image_pull_policy=ImagePullPolicy.always)._build_image_pull_policy()
            == ImagePullPolicy.always
        )
        assert ContainerMixin()._build_image_pull_policy() is None
