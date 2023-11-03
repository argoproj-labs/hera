from hera.workflows.env import Env
from hera.workflows.env_from import SecretEnvFrom
from hera.workflows.models import EnvFromSource, EnvVar, ImagePullPolicy, Quantity, ResourceRequirements
from hera.workflows.resources import Resources
from hera.workflows.user_container import UserContainer


class TestUserContainer:
    def test_build_image_pull_policy(self) -> None:
        assert UserContainer(name="test", image_pull_policy="Always")._build_image_pull_policy() == "Always"
        assert (
            UserContainer(name="test", image_pull_policy=ImagePullPolicy.always)._build_image_pull_policy() == "Always"
        )
        assert UserContainer(name="test")._build_image_pull_policy() is None

    def test_build_resources(self) -> None:
        r = UserContainer(name="test", resources=Resources(cpu_request=1))._build_resources()
        assert "cpu" in r.requests
        assert r.requests["cpu"] == Quantity(__root__="1")

        r = UserContainer(
            name="test", resources=ResourceRequirements(limits={"cpu": Quantity(__root__="1")})
        )._build_resources()
        assert "cpu" in r.limits
        assert r.limits["cpu"] == Quantity(__root__="1")

    def test_builds_env(self) -> None:
        e = UserContainer(name="test", env=Env(name="test", value="test"))._build_env()
        assert len(e) == 1
        assert isinstance(e[0], EnvVar)
        assert e[0].name == "test"
        assert e[0].value == "test"

        e = UserContainer(name="test", env=EnvVar(name="test", value="test"))._build_env()
        assert isinstance(e[0], EnvVar)
        assert e[0].name == "test"
        assert e[0].value == "test"

        e = UserContainer(
            name="test",
            env=[
                Env(name="test1", value="test1"),
                EnvVar(name="test2", value="test2"),
            ],
        )._build_env()
        assert isinstance(e[0], EnvVar)
        assert e[0].name == "test1"
        assert e[0].value == "test1"
        assert isinstance(e[1], EnvVar)
        assert e[1].name == "test2"
        assert e[1].value == "test2"

    def test_builds_env_from(self) -> None:
        e = UserContainer(name="test", env_from=SecretEnvFrom(name="test"))._build_env_from()
        assert len(e) == 1
        assert isinstance(e[0], EnvFromSource)
        assert e[0].secret_ref is not None
        assert e[0].secret_ref.name == "test"

        e = UserContainer(name="test", env_from=EnvFromSource(secret_ref=SecretEnvFrom(name="test")))._build_env_from()
        assert len(e) == 1
        assert isinstance(e[0], EnvFromSource)
        assert e[0].secret_ref is not None
        assert e[0].secret_ref.name == "test"

        e = UserContainer(
            name="test",
            env_from=[
                SecretEnvFrom(name="test1"),
                EnvFromSource(secret_ref=SecretEnvFrom(name="test2")),
            ],
        )._build_env_from()
        assert len(e) == 2
        assert isinstance(e[0], EnvFromSource)
        assert e[0].secret_ref is not None
        assert e[0].secret_ref.name == "test1"
        assert isinstance(e[1], EnvFromSource)
        assert e[1].secret_ref is not None
        assert e[1].secret_ref.name == "test2"
