"""The unit tests of the Artifact class, covering the name: Optional[str] behaviour."""

import pytest

from hera.workflows.artifact import Artifact


def test_artifact_no_name_can_be_created():
    artifact = Artifact(path="tmp/path")
    assert artifact


def test_artifact_no_name_fails_build_artifact():
    artifact = Artifact(path="tmp/path")
    with pytest.raises(ValueError) as e:
        artifact._build_artifact()

    assert "name cannot be `None` or empty when used" in str(e.value)


def test_artifact_no_name_fails_build_artifact_paths():
    artifact = Artifact(path="tmp/path")
    with pytest.raises(ValueError) as e:
        artifact._build_artifact_paths()

    assert "name cannot be `None` or empty when used" in str(e.value)


def test_artifact_no_name_fails_as_name():
    artifact = Artifact(path="tmp/path")
    with pytest.raises(ValueError) as e:
        artifact.as_name("my_art")

    assert "name cannot be `None` or empty when used" in str(e.value)
