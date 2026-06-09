"""The unit tests of the Artifact class, covering the name: Optional[str] behaviour."""

import pytest

from hera.workflows.artifact import Artifact, PluginArtifact


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
