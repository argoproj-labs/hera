from typing import List, Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GCSArtifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
    IoArgoprojWorkflowV1alpha1HTTPArtifact,
    IoArgoprojWorkflowV1alpha1S3Artifact,
    SecretKeySelector,
)


class Artifact:
    """An artifact represents an object that Argo creates for a specific task's output.

    The output of a task payload can store specific results at a path, which can then be consumed by
    another dependent task.

    Attributes
    ----------
    name: str
        The name of the artifact.
    path: str
        The path to the file to be assembled into an artifact. This path is relative to the task environment.
        If clients have a volume where results are stored, it's the path to the created object on the
        respective volume.

    Notes
    -----
    Don't use this directly. Use OutputArtifact, InputArtifact, etc.
    """

    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.path = path

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Constructs the corresponding Argo artifact representation"""
        return IoArgoprojWorkflowV1alpha1Artifact(name=self.name, path=self.path)

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Artifact representation for setting task inputs"""
        return IoArgoprojWorkflowV1alpha1Artifact(name=self.name, path=self.path)


class OutputArtifact(Artifact):
    """An output artifact representation"""

    pass


class InputArtifact(Artifact):
    """An input artifact representation.

    This artifact is used to represent a task's input from the output of another task's artifact.

    Attributes
    ----------
    name: str
        The name of the input artifact.
    path: str
        The path where to store the input artifact. Note that this path is isolated from the output artifact path
        of the previous task artifact.
    from_task: str
        Name of the task whose artifact this artifact represents.
    artifact_name: str
        Name of the artifact to consume from the previous task.
    """

    def __init__(self, name: str, path: str, from_task: str, artifact_name: str) -> None:
        self.from_task = from_task
        self.artifact_name = artifact_name
        super(InputArtifact, self).__init__(name, path)

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Constructs the corresponding Argo artifact representation"""
        from_ = f"{{{{tasks.{self.from_task}.outputs.artifacts.{self.artifact_name}}}}}"
        return IoArgoprojWorkflowV1alpha1Artifact(name=self.name, path=self.path, _from=from_)


class BucketArtifact(Artifact):
    """An input artifact representation.

    This artifact is used to represent a bucket object

    Attributes
    ----------
    name: str
        The name of the input artifact.
    path: str
        The path where to store the input artifact. Note that this path is isolated from the output artifact path
        of the previous task artifact.
    bucket: str
        The name of the bucket to fetch the artifact from.
    key: str
        Key of the artifact in the bucket.

    Notes
    -----
    Don't use this directly. Use S3InputArtifact or GCSInputArtifact
    """

    def __init__(self, name: str, path: str, bucket: str, key: str) -> None:
        self.bucket = bucket
        self.key = key
        super(BucketArtifact, self).__init__(name, path)


class S3Artifact(BucketArtifact):
    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            s3=IoArgoprojWorkflowV1alpha1S3Artifact(bucket=self.bucket, key=self.key),
        )

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return self.get_spec()


class GCSArtifact(BucketArtifact):
    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            gcs=IoArgoprojWorkflowV1alpha1GCSArtifact(bucket=self.bucket, key=self.key),
        )

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return self.get_spec()


class GitArtifact(Artifact):
    """ """

    repo: str
    revision: Optional[str]

    def __init__(
        self,
        name: str,
        path: str,
        repo: str,
        revision: Optional[str] = None,
        depth: Optional[int] = None,
        disable_submodules: Optional[bool] = None,
        fetch: Optional[List[str]] = None,
        insecure_ignore_host_key: Optional[bool] = None,
        username_secret_key: Optional[str] = None,
        username_secret_name: Optional[str] = None,
        password_secret_key: Optional[str] = None,
        password_secret_name: Optional[str] = None,
        ssh_private_key_secret_key: Optional[str] = None,
        ssh_private_key_secret_name: Optional[str] = None,
    ) -> None:
        self.repo = repo
        self.depth = depth
        self.disable_submodules = disable_submodules
        self.fetch = fetch
        self.insecure_ignore_host_key = insecure_ignore_host_key
        self.username_secret_key = username_secret_key
        self.username_secret_name = username_secret_name
        self.password_secret_key = password_secret_key
        self.password_secret_name = password_secret_name
        self.revision = revision
        self.ssh_private_key_secret_key = ssh_private_key_secret_key
        self.ssh_private_key_secret_name = ssh_private_key_secret_name
        super(GitArtifact, self).__init__(name, path)

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        git = IoArgoprojWorkflowV1alpha1GitArtifact(repo=self.repo)
        if self.depth is not None:
            setattr(git, "depth", self.depth)
        if self.disable_submodules is not None:
            setattr(git, "disable_submodules", self.disable_submodules)
        if self.fetch is not None:
            setattr(git, "fetch", self.fetch)
        if self.insecure_ignore_host_key is not None:
            setattr(git, "insecure_ignore_host_key", self.insecure_ignore_host_key)
        if self.password_secret_key is not None:
            password_secret = SecretKeySelector(key=self.password_secret_key)
            if self.password_secret_name is not None:
                setattr(password_secret, "name", self.password_secret_name)
            setattr(git, "password_secret", password_secret)
        if self.revision:
            setattr(git, "revision", self.revision)
        if self.ssh_private_key_secret_name is not None:
            ssh_private_key_secret = SecretKeySelector(key=self.ssh_private_key_secret_key)
            if self.password_secret_name is not None:
                setattr(ssh_private_key_secret, "name", self.ssh_private_key_secret_name)
            setattr(git, "ssh_private_key_secret", ssh_private_key_secret)
        if self.username_secret_key is not None:
            username_secret = SecretKeySelector(key=self.username_secret_key)
            if self.username_secret_name is not None:
                setattr(username_secret, "name", self.username_secret_name)
            setattr(git, "username_secret", username_secret)
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            git=git,
        )

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return self.get_spec()


class HttpArtifact(Artifact):
    url: str

    def __init__(self, name: str, path: str, url: str) -> None:
        self.url = url
        super(HttpArtifact, self).__init__(name, path)

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            http=IoArgoprojWorkflowV1alpha1HTTPArtifact(url=self.url),
        )

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return self.get_spec()
