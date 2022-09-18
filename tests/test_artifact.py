from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
    IoArgoprojWorkflowV1alpha1HTTPArtifact,
)

from hera import Artifact, GitArtifact, HttpArtifact, Task


def test_output_artifact_contains_expected_fields():
    name = "test-artifact"
    path = "/input/path"
    from_task = "produce-artifact"

    expected = Artifact(name=name, path=path, from_task=f"{{{{tasks.{from_task}.outputs.artifacts.{name}}}}}")
    t1 = Task("produce-artifact", outputs=[Artifact(name, path)])
    actual = t1.get_artifact(name)

    assert isinstance(actual, Artifact)
    assert actual.from_task == expected.from_task
    assert actual.name == expected.name
    assert actual.path == expected.path

    new_path = "/input/alternative_path"
    expected = Artifact(name=name, path=new_path, from_task=f"{{{{tasks.{from_task}.outputs.artifacts.{name}}}}}")
    actual = t1.get_artifact(name).to_path(new_path)
    assert isinstance(actual, Artifact)
    assert actual.from_task == expected.from_task
    assert actual.name == expected.name
    assert actual.path == expected.path

    new_name = "test-artifact2"
    expected = Artifact(name=new_name, path=new_path, from_task=f"{{{{tasks.{from_task}.outputs.artifacts.{name}}}}}")
    actual = t1.get_artifact(name).to_path(new_path).as_name(new_name)
    assert isinstance(actual, Artifact)
    assert actual.from_task == expected.from_task
    assert actual.name == expected.name
    assert actual.path == expected.path


def test_git_artifact():
    name = "git-artifact"
    path = "/src"
    repo = "https://github.com/awesome/awesome-repo.git"
    revision = "main"

    expected = IoArgoprojWorkflowV1alpha1Artifact(
        name=name, path=path, git=IoArgoprojWorkflowV1alpha1GitArtifact(repo=repo, revision=revision)
    )
    actual = GitArtifact(name, path, repo, revision).as_argument()
    actual_input = GitArtifact(name, path, repo, revision).as_input()

    assert actual == expected
    assert actual_input == expected


def test_http_artifact():
    name = "http-artifact"
    path = "/src"
    url = "whatever.com/my-file.txt"

    expected = IoArgoprojWorkflowV1alpha1Artifact(
        name=name, path=path, http=IoArgoprojWorkflowV1alpha1HTTPArtifact(url=url)
    )
    actual = HttpArtifact(name, path, url).as_argument()
    actual_input = HttpArtifact(name, path, url).as_input()

    assert actual == expected
    assert actual_input == expected
