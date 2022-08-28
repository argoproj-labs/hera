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
    actual = GitArtifact(name, path, repo, revision=revision).get_spec()
    actual_input = GitArtifact(name, path, repo, revision=revision).get_input_spec()

    assert actual == expected
    assert actual_input == expected


def test_git_artifact_uses_secrets():
    artifact = GitArtifact(
        "test",
        "/path",
        "repo",
        revision="main",
        depth=1,
        disable_submodules=True,
        fetch=["a", "b"],
        insecure_ignore_host_key=False,
        password_secret_key="password-secret-key",
        password_secret_name="password-secret-name",
        ssh_private_key_secret_key="ssh-key",
        ssh_private_key_secret_name="ssh-name",
        username_secret_key="username-secret-key",
        username_secret_name="username-secret-name",
    ).get_spec()

    assert artifact.name == "test"
    assert artifact.path == "/path"
    assert artifact.git.repo == "repo"
    assert artifact.git.revision == "main"
    assert artifact.git.depth == 1
    assert artifact.git.disable_submodules is True
    assert artifact.git.fetch == ["a", "b"]
    assert artifact.git.insecure_ignore_host_key is False
    assert artifact.git.password_secret.key == "password-secret-key"
    assert artifact.git.password_secret.name == "password-secret-name"
    assert artifact.git.ssh_private_key_secret.key == "ssh-key"
    assert artifact.git.ssh_private_key_secret.name == "ssh-name"
    assert artifact.git.username_secret.key == "username-secret-key"
    assert artifact.git.username_secret.name == "username-secret-name"


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
