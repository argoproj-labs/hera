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


def test_plugin_artifact_builds_model_with_plugin_field():
    artifact = PluginArtifact(
        name="output",
        path="/tmp/output",
        key="results.json",
        plugin_name="oras",
        configuration="image: registry.example.com/my-image",
        connection_timeout_seconds=30,
    )._build_artifact()

    assert artifact.plugin is not None
    assert artifact.plugin.key == "results.json"
    assert artifact.plugin.name == "oras"
    assert artifact.plugin.configuration == "image: registry.example.com/my-image"
    assert artifact.plugin.connection_timeout_seconds == 30


def test_plugin_artifact_serializes_camelcase_alias():
    """The wire format uses camelCase per the Argo OpenAPI spec; the Python field is snake_case."""
    artifact = PluginArtifact(
        name="output",
        path="/tmp/output",
        key="results.json",
        connection_timeout_seconds=15,
    )._build_artifact()

    dumped = artifact.model_dump(by_alias=True, exclude_none=True)
    assert dumped["plugin"]["connectionTimeoutSeconds"] == 15
    assert "connection_timeout_seconds" not in dumped["plugin"]
