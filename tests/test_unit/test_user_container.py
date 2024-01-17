from hera.workflows.models import (
    ImagePullPolicy,
    UserContainer as ModelUserContainer,
    VolumeMount,
)
from hera.workflows.user_container import UserContainer
from hera.workflows.volume import Volume


class TestUserContainer:
    def test_build_image_pull_policy(self) -> None:
        assert UserContainer(name="test", image_pull_policy="Always")._build_image_pull_policy() == "Always"
        assert (
            UserContainer(name="test", image_pull_policy=ImagePullPolicy.always)._build_image_pull_policy() == "Always"
        )
        assert UserContainer(name="test")._build_image_pull_policy() is None

    def test_builds_volume_mounts(self) -> None:
        uc: ModelUserContainer = UserContainer(
            name="test", volume_mounts=[VolumeMount(name="test", mount_path="/test")]
        ).build()
        assert isinstance(uc, ModelUserContainer)
        assert uc.volume_mounts is not None
        assert len(uc.volume_mounts) == 1
        assert uc.volume_mounts[0].name == "test"
        assert uc.volume_mounts[0].mount_path == "/test"

        uc: ModelUserContainer = UserContainer(
            name="test", volumes=[Volume(name="test", mount_path="/test", size="1Gi")]
        ).build()
        assert isinstance(uc, ModelUserContainer)
        assert uc.volume_mounts is not None
        assert len(uc.volume_mounts) == 1
        assert uc.volume_mounts[0].name == "test"
        assert uc.volume_mounts[0].mount_path == "/test"

        uc: ModelUserContainer = UserContainer(
            name="test",
            volume_mounts=[VolumeMount(name="test1", mount_path="/test1")],
            volumes=[Volume(name="test2", mount_path="/test2", size="1Gi")],
        ).build()
        assert isinstance(uc, ModelUserContainer)
        assert uc.volume_mounts is not None
        assert len(uc.volume_mounts) == 2
        assert uc.volume_mounts[0].name == "test1"
        assert uc.volume_mounts[0].mount_path == "/test1"
        assert uc.volume_mounts[1].name == "test2"
        assert uc.volume_mounts[1].mount_path == "/test2"
