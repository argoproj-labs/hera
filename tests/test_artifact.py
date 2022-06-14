from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
)

from hera import GitArtifact, InputArtifact, OutputArtifact


def test_output_artifact_contains_expected_fields():
    name = 'output'
    path = '/output/path'
    expected = IoArgoprojWorkflowV1alpha1Artifact(name=name, path=path)
    actual = OutputArtifact(name=name, path=path).get_spec()
    assert actual.name == expected.name
    assert actual.path == expected.path


def test_input_artifact_contains_expected_fields():
    name = 'input'
    path = '/input/path'
    from_task = 'test'
    artifact_name = 'test-artifact'
    expected = IoArgoprojWorkflowV1alpha1Artifact(
        name=name, path=path, _from=f"{{{{tasks.{from_task}.outputs.artifacts.{artifact_name}}}}}"
    )
    actual = InputArtifact(name=name, path=path, from_task=from_task, artifact_name=artifact_name).get_spec()
    assert actual.name == expected.name
    assert actual.path == expected.path
    assert actual._from == expected._from


def test_git_artifact():
    name = "git-artifact"
    path = "/src"
    repo = "https://github.com/awesome/awesome-repo.git"
    revision = "main"

    expected = IoArgoprojWorkflowV1alpha1Artifact(
        name=name, path=path, git=IoArgoprojWorkflowV1alpha1GitArtifact(repo=repo, revision=revision)
    )
    actual = GitArtifact(name=name, path=path, repo=repo, revision=revision).get_spec()

    assert actual == expected
