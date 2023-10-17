from hera.workflows.models import ImagePullPolicy
from hera.workflows.user_container import UserContainer


class TestUserContainer:
    def test_build_image_pull_policy(self) -> None:
        assert UserContainer(name="test", image_pull_policy="Always")._build_image_pull_policy() == "Always"
        assert (
            UserContainer(name="test", image_pull_policy=ImagePullPolicy.always)._build_image_pull_policy() == "Always"
        )
        assert UserContainer(name="test")._build_image_pull_policy() is None
