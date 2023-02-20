from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1ArchiveStrategy,
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GCSArtifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
    IoArgoprojWorkflowV1alpha1HTTPArtifact,
    IoArgoprojWorkflowV1alpha1RawArtifact,
    IoArgoprojWorkflowV1alpha1S3Artifact,
    SecretKeySelector,
)

from hera.workflows import (
    Archive,
    Artifact,
    GCSArtifact,
    GitArtifact,
    HttpArtifact,
    RawArtifact,
    S3Artifact,
    Task,
)


class TestArtifact:
    def test_as_argument_returns_expected_artifact(self):
        artifact = Artifact("a", from_task="b", path="/a", sub_path="/b/c")
        argument = artifact.as_argument()
        assert isinstance(argument, IoArgoprojWorkflowV1alpha1Artifact)
        assert argument.name == "a"
        assert hasattr(argument, "_from")
        assert argument._from == "b"
        assert hasattr(argument, "sub_path")
        assert argument.sub_path == "/b/c"

        artifact = Artifact("a", path="/a")
        argument = artifact.as_argument()
        assert isinstance(argument, IoArgoprojWorkflowV1alpha1Artifact)
        assert argument.name == "a"
        assert not hasattr(argument, "_from")
        assert not hasattr(argument, "sub_path")

    def test_as_output_returns_expected_artifact(self):
        artifact = Artifact("a", path="/a", archive=Archive(disable_compression=True))
        argument = artifact.as_output()
        assert isinstance(argument, IoArgoprojWorkflowV1alpha1Artifact)
        assert argument.name == "a"
        assert hasattr(argument, "archive")
        assert isinstance(argument.archive, IoArgoprojWorkflowV1alpha1ArchiveStrategy)
        assert hasattr(argument.archive, "none")

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
        artifact = S3Artifact("a", "s3://test", "test", "test", Archive(zip=True))
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
        assert argument.archive.zip

    def test_as_output_returns_expected_output(self):
        artifact = S3Artifact("a", "s3://test", "test", "test", Archive(zip=True))
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
        assert output.archive.zip


class TestGCSArtifact:
    def test_as_argument_returns_expected_argument(self):
        artifact = GCSArtifact("a", "gs://test", "test", "test", Archive(zip=True))
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
        assert argument.archive.zip

    def test_as_output_returns_expected_output(self):
        artifact = GCSArtifact("a", "gs://test", "test", "test", Archive(zip=True))
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
        assert output.archive.zip


class TestGitArtifact:
    def test_as_argument_returns_expected_output(self):
        artifact = GitArtifact("git-artifact", "/src", "https://github.com/awesome/awesome-repo.git").as_argument()
        assert isinstance(artifact, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(artifact, "name")
        assert artifact.name == "git-artifact"
        assert hasattr(artifact, "path")
        assert artifact.path == "/src"
        assert hasattr(artifact, "git")
        assert isinstance(artifact.git, IoArgoprojWorkflowV1alpha1GitArtifact)
        assert hasattr(artifact.git, "repo")
        assert artifact.git.repo == "https://github.com/awesome/awesome-repo.git"
        assert not hasattr(artifact.git, "depth")
        assert not hasattr(artifact.git, "disable_submodules")
        assert not hasattr(artifact.git, "fetch")
        assert not hasattr(artifact.git, "insecure_ignore_host_key")
        assert not hasattr(artifact.git, "password_secret")
        assert not hasattr(artifact.git, "revision")
        assert not hasattr(artifact.git, "ssh_private_key_secret")
        assert not hasattr(artifact.git, "username_secret")

        artifact = GitArtifact(
            "git-artifact",
            "/src",
            "https://github.com/awesome/awesome-repo.git",
            revision="abc",
            depth=2,
            disable_submodules=True,
            fetch=["a", "b", "c"],
            insecure_ignore_host_key=True,
            username_secret_name="abc",
            username_secret_key="key",
            password_secret_name="abc",
            password_secret_key="key",
            ssh_private_key_secret_name="abc",
            ssh_private_key_secret_key="key",
        ).as_argument()
        assert isinstance(artifact, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(artifact, "name")
        assert artifact.name == "git-artifact"
        assert hasattr(artifact, "path")
        assert artifact.path == "/src"
        assert hasattr(artifact, "git")
        assert isinstance(artifact.git, IoArgoprojWorkflowV1alpha1GitArtifact)
        assert hasattr(artifact.git, "repo")
        assert artifact.git.repo == "https://github.com/awesome/awesome-repo.git"
        assert hasattr(artifact.git, "depth")
        assert artifact.git.depth == 2
        assert hasattr(artifact.git, "disable_submodules")
        assert artifact.git.disable_submodules
        assert hasattr(artifact.git, "fetch")
        assert artifact.git.fetch == ["a", "b", "c"]
        assert hasattr(artifact.git, "insecure_ignore_host_key")
        assert artifact.git.insecure_ignore_host_key
        assert hasattr(artifact.git, "username_secret")
        assert isinstance(artifact.git.username_secret, SecretKeySelector)
        assert artifact.git.username_secret.key == "key"
        assert hasattr(artifact.git.username_secret, "name")
        assert artifact.git.username_secret.name == "abc"
        assert hasattr(artifact.git, "password_secret")
        assert isinstance(artifact.git.password_secret, SecretKeySelector)
        assert artifact.git.password_secret.key == "key"
        assert hasattr(artifact.git.password_secret, "name")
        assert artifact.git.password_secret.name == "abc"
        assert hasattr(artifact.git, "ssh_private_key_secret")
        assert isinstance(artifact.git.ssh_private_key_secret, SecretKeySelector)
        assert artifact.git.ssh_private_key_secret.key == "key"
        assert hasattr(artifact.git.ssh_private_key_secret, "name")
        assert artifact.git.ssh_private_key_secret.name == "abc"
        assert hasattr(artifact.git, "revision")
        assert artifact.git.revision == "abc"

        artifact = GitArtifact(
            "git-artifact",
            "/src",
            "https://github.com/awesome/awesome-repo.git",
            revision="abc",
            depth=2,
            disable_submodules=True,
            fetch=["a", "b", "c"],
            insecure_ignore_host_key=True,
            username_secret_key="key",
            password_secret_key="key",
            ssh_private_key_secret_key="key",
        ).as_argument()
        assert isinstance(artifact, IoArgoprojWorkflowV1alpha1Artifact)
        assert hasattr(artifact, "name")
        assert artifact.name == "git-artifact"
        assert hasattr(artifact, "path")
        assert artifact.path == "/src"
        assert hasattr(artifact, "git")
        assert isinstance(artifact.git, IoArgoprojWorkflowV1alpha1GitArtifact)
        assert hasattr(artifact.git, "repo")
        assert artifact.git.repo == "https://github.com/awesome/awesome-repo.git"
        assert hasattr(artifact.git, "depth")
        assert artifact.git.depth == 2
        assert hasattr(artifact.git, "disable_submodules")
        assert artifact.git.disable_submodules
        assert hasattr(artifact.git, "fetch")
        assert artifact.git.fetch == ["a", "b", "c"]
        assert hasattr(artifact.git, "insecure_ignore_host_key")
        assert artifact.git.insecure_ignore_host_key
        assert hasattr(artifact.git, "username_secret")
        assert isinstance(artifact.git.username_secret, SecretKeySelector)
        assert artifact.git.username_secret.key == "key"
        assert not hasattr(artifact.git.username_secret, "name")
        assert hasattr(artifact.git, "password_secret")
        assert isinstance(artifact.git.password_secret, SecretKeySelector)
        assert artifact.git.password_secret.key == "key"
        assert not hasattr(artifact.git.password_secret, "name")
        assert hasattr(artifact.git, "ssh_private_key_secret")
        assert isinstance(artifact.git.ssh_private_key_secret, SecretKeySelector)
        assert artifact.git.ssh_private_key_secret.key == "key"
        assert not hasattr(artifact.git.ssh_private_key_secret, "name")
        assert hasattr(artifact.git, "revision")
        assert artifact.git.revision == "abc"


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


class TestRawArtifact:
    def test_as_input_returns_expected_artifact(self):
        name = "toupie"
        path = "/abc"
        data = "foobar"
        raw = IoArgoprojWorkflowV1alpha1RawArtifact(data=data)
        artifact = RawArtifact(name, path=path, data=data)
        input = artifact.as_input()
        assert isinstance(input, IoArgoprojWorkflowV1alpha1Artifact)
        assert input.name == name
        assert hasattr(input, "path")
        assert input.path == path
        assert hasattr(input, "raw")
        assert input.raw == raw
