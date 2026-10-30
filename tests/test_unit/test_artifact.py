"""The unit tests of the Artifact class, covering the name: Optional[str] behaviour."""

from dataclasses import fields

import pytest

from hera.workflows.artifact import Artifact, GitArtifact, OSSArtifact, PluginArtifact, S3Artifact
from hera.workflows.models import SecretKeySelector


def test_artifact_no_name_can_be_created():
    artifact = Artifact(path="/tmp/path")
    assert artifact


def test_artifact_no_name_fails_build_artifact():
    artifact = Artifact(path="/tmp/path")
    with pytest.raises(ValueError) as e:
        artifact._build_artifact()

    assert "name cannot be `None` or empty when used" in str(e.value)


def test_artifact_no_name_fails_build_artifact_paths():
    artifact = Artifact(path="/tmp/path")
    with pytest.raises(ValueError) as e:
        artifact._build_artifact_paths()

    assert "name cannot be `None` or empty when used" in str(e.value)


def test_artifact_no_name_passes_with_name():
    artifact = Artifact(path="/tmp/path")
    assert artifact.with_name("new") == Artifact(name="new", path="/tmp/path")


def test_plugin_artifact_build_populates_plugin_field():
    artifact = PluginArtifact(
        name="my-artifact",
        path="/tmp/out",
        key="data/v1",
        plugin_name="my-driver",
        configuration='{"region": "eu-west-1"}',
        connection_timeout_seconds=30,
    )

    built = artifact._build_artifact()

    assert built.name == "my-artifact"
    assert built.path == "/tmp/out"
    assert built.plugin is not None
    assert built.plugin.key == "data/v1"
    assert built.plugin.name == "my-driver"
    assert built.plugin.configuration == '{"region": "eu-west-1"}'
    assert built.plugin.connection_timeout_seconds == 30


def test_plugin_artifact_input_attributes_extend_base():
    attrs = PluginArtifact._get_input_attributes()

    for base_attr in Artifact._get_input_attributes():
        assert base_attr in attrs
    for extra in ("configuration", "connection_timeout_seconds", "key", "plugin_name"):
        assert extra in attrs


def test_git_artifact_build_passes_insecure_skip_tls():
    built = GitArtifact(
        name="a", path="/tmp/a", repo="https://example.com/r.git", insecure_skip_tls=True
    )._build_artifact()

    assert built.git is not None
    assert built.git.insecure_skip_tls is True


def test_oss_artifact_build_passes_use_sdk_creds():
    built = OSSArtifact(name="a", path="/tmp/a", key="k", use_sdk_creds=True)._build_artifact()

    assert built.oss is not None
    assert built.oss.use_sdk_creds is True


def test_s3_artifact_build_passes_ca_and_session_token_secrets():
    ca_secret = SecretKeySelector(name="s3-ca", key="ca.crt")
    session_token_secret = SecretKeySelector(name="s3-creds", key="sessionToken")

    built = S3Artifact(
        name="a", path="/tmp/a", key="k", ca_secret=ca_secret, session_token_secret=session_token_secret
    )._build_artifact()

    assert built.s3 is not None
    assert built.s3.ca_secret == ca_secret
    assert built.s3.session_token_secret == session_token_secret


@pytest.mark.parametrize(
    "artifact_class",
    [cls for cls in Artifact.__subclasses__() if "_get_input_attributes" in cls.__dict__],
    ids=lambda cls: cls.__name__,
)
def test_artifact_input_attributes_cover_all_fields(artifact_class):
    base_fields = {f.name for f in fields(Artifact)}
    own_fields = {f.name for f in fields(artifact_class)} - base_fields

    assert own_fields <= set(artifact_class._get_input_attributes())
