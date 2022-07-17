from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
    IoArgoprojWorkflowV1alpha1HTTPArtifact,
)

from hera import GitArtifact, HttpArtifact, InputArtifact, OutputArtifact


def test_output_artifact_contains_expected_fields():
    name = "output"
    path = "/output/path"
    expected = IoArgoprojWorkflowV1alpha1Artifact(name=name, path=path)
    actual = OutputArtifact(name, path).get_spec()
    actual_input = OutputArtifact(name, path).get_input_spec()

    assert actual.name == expected.name
    assert actual.path == expected.path
    assert actual_input.name == expected.name
    assert actual_input.path == expected.path


def test_input_artifact_contains_expected_fields():
    name = "input"
    path = "/input/path"
    from_task = "test"
    artifact_name = "test-artifact"
    expected = IoArgoprojWorkflowV1alpha1Artifact(
        name=name, path=path, _from=f"{{{{tasks.{from_task}.outputs.artifacts.{artifact_name}}}}}"
    )
    actual = InputArtifact(name, path, from_task, artifact_name).get_spec()
    actual_input = InputArtifact(name, path, from_task, artifact_name).get_input_spec()
    assert actual.name == expected.name
    assert actual.path == expected.path
    assert actual._from == expected._from
    assert actual_input.name == expected.name
    assert actual_input.path == expected.path
    assert not hasattr(actual_input, "_from")


def test_git_artifact():
    name = "git-artifact"
    path = "/src"
    repo = "https://github.com/awesome/awesome-repo.git"
    revision = "main"

    expected = IoArgoprojWorkflowV1alpha1Artifact(
        name=name, path=path, git=IoArgoprojWorkflowV1alpha1GitArtifact(repo=repo, revision=revision)
    )
    actual = GitArtifact(name, path, repo, revision).get_spec()
    actual_input = GitArtifact(name, path, repo, revision).get_input_spec()

    assert actual == expected
    assert actual_input == expected


def test_http_artifact():
    name = "http-artifact"
    path = "/src"
    url = "whatever.com/my-file.txt"

    expected = IoArgoprojWorkflowV1alpha1Artifact(
        name=name, path=path, http=IoArgoprojWorkflowV1alpha1HTTPArtifact(url=url)
    )
    actual = HttpArtifact(name, path, url).get_spec()
    actual_input = HttpArtifact(name, path, url).get_input_spec()

    assert actual == expected
    assert actual_input == expected
