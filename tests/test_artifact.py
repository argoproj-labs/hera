from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1ArchiveStrategy,
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GCSArtifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
    IoArgoprojWorkflowV1alpha1HTTPArtifact,
    IoArgoprojWorkflowV1alpha1S3Artifact,
    SecretKeySelector,
)

from hera import Artifact, GCSArtifact, GitArtifact, HttpArtifact, S3Artifact, Task


class TestArtifact:
    def test_artifact_as_argument_returns_expected_artifact(self):
        artifact = Artifact("a", from_task="b", path="/a", sub_path="/b/c")
        argument = artifact.as_argument()
        assert isinstance(argument, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(argument, "_from")
        assert argument._from == "b"
        assert hasattr(argument, "sub_path")
        assert argument.sub_path == "/b/c"

    def test_output_artifact_contains_expected_fields(self):
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
        expected = Artifact(
            name=new_name, path=new_path, from_task=f"{{{{tasks.{from_task}.outputs.artifacts.{name}}}}}"
        )
        actual = t1.get_artifact(name).to_path(new_path).as_name(new_name)
        assert isinstance(actual, Artifact)
        assert actual.from_task == expected.from_task
        assert actual.name == expected.name
        assert actual.path == expected.path


class TestS3Artifact:
    def test_as_argument_returns_expected_argument(self):
        artifact = S3Artifact("a", "s3://test", "test", "test", archive={"zip": "test"})
        argument = artifact.as_argument()
        assert isinstance(argument, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(argument, "name")
        assert argument.name == "a"
        assert hasattr(argument, "path")
        assert argument.path == "s3://test"
        assert hasattr(argument, "s3")
        assert isinstance(argument.s3, IoArgoprojWorkflowV1alpha1S3Artifact)
        assert argument.s3.bucket == "test"
        assert argument.s3.key == "test"
        assert hasattr(argument, "archive")
        assert isinstance(argument.archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(argument.archive, "zip")
        assert argument.archive.zip == "test"

    def test_as_output_returns_expected_output(self):
        artifact = S3Artifact("a", "s3://test", "test", "test", archive={"zip": "test"})
        output = artifact.as_output()
        assert isinstance(output, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(output, "name")
        assert output.name == "a"
        assert hasattr(output, "path")
        assert output.path == "s3://test"
        assert hasattr(output, "s3")
        assert isinstance(output.s3, IoArgoprojWorkflowV1alpha1S3Artifact)
        assert output.s3.bucket == "test"
        assert output.s3.key == "test"
        assert hasattr(output, "archive")
        assert isinstance(output.archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(output.archive, "zip")
        assert output.archive.zip == "test"


class TestGCSArtifact:
    def test_as_argument_returns_expected_argument(self):
        artifact = GCSArtifact("a", "gs://test", "test", "test", archive={"zip": "test"})
        argument = artifact.as_argument()
        assert isinstance(argument, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(argument, "name")
        assert argument.name == "a"
        assert hasattr(argument, "path")
        assert argument.path == "gs://test"
        assert hasattr(argument, "gcs")
        assert isinstance(argument.gcs, IoArgoprojWorkflowV1alpha1GCSArtifact)
        assert argument.gcs.bucket == "test"
        assert argument.gcs.key == "test"
        assert hasattr(argument, "archive")
        assert isinstance(argument.archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(argument.archive, "zip")
        assert argument.archive.zip == "test"

    def test_as_output_returns_expected_output(self):
        artifact = GCSArtifact("a", "gs://test", "test", "test", archive={"zip": "test"})
        output = artifact.as_output()
        assert isinstance(output, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(output, "name")
        assert output.name == "a"
        assert hasattr(output, "path")
        assert output.path == "gs://test"
        assert hasattr(output, "gcs")
        assert isinstance(output.gcs, IoArgoprojWorkflowV1alpha1GCSArtifact)
        assert output.gcs.bucket == "test"
        assert output.gcs.key == "test"
        assert hasattr(output, "archive")
        assert isinstance(output.archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(output.archive, "zip")
        assert output.archive.zip == "test"


class TestGitArtifact:
    def test_git_artifact_returns_expected_output(self):
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

    def test_git_artifact_ssh_key_secret(self):
        name = "git-artifact"
        path = "/src"
        repo = "https://github.com/awesome/awesome-repo.git"
        revision = "main"
        # name of the secret
        secret_name = "git-ssh-key"
        # key in secret
        secret_key = "ssh-key"
        secret_key_selector = SecretKeySelector(key=secret_key, name=secret_name)
        expected = IoArgoprojWorkflowV1alpha1Artifact(
            name=name,
            path=path,
            git=IoArgoprojWorkflowV1alpha1GitArtifact(
                repo=repo, revision=revision, ssh_private_key_secret=secret_key_selector
            ),
        )
        actual = GitArtifact(
            name=name,
            path=path,
            repo=repo,
            revision=revision,
            ssh_private_key_secret_key=secret_key,
            ssh_private_key_secret_name=secret_name,
        )
        assert actual.as_argument() == expected
        assert actual.as_input() == expected


class TestHTTPArtifact:
    def test_http_artifact_returns_expected_output(self):
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
