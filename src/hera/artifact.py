from typing import List, Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GCSArtifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
    IoArgoprojWorkflowV1alpha1HTTPArtifact,
    IoArgoprojWorkflowV1alpha1S3Artifact,
    SecretKeySelector,
)

from hera.archive import Archive


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
    from_task: Optional[str] = None
        The name of the task that generates the artifact.
    """

    def __init__(self, name: str, path: str, from_task: Optional[str] = None, sub_path: Optional[str] = None) -> None:
        self.name = name
        self.path = path
        self.from_task = from_task
        self.sub_path = sub_path

    def as_name(self, name: str):
        """Changes the name of the artifact."""
        self.name = name
        return self

    def to_path(self, path: str, sub_path: Optional[str] = None):
        """Change the paths of the artifact"""
        self.path = path
        self.sub_path = sub_path
        return self

    def as_argument(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact specifications for use as an argument to a task"""
        artifact = IoArgoprojWorkflowV1alpha1Artifact(name=self.name)
        if self.from_task is not None:
            setattr(artifact, "_from", self.from_task)
        if self.sub_path:
            setattr(artifact, "sub_path", self.sub_path)
        return artifact

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact specifications for use as an input to a task"""
        return IoArgoprojWorkflowV1alpha1Artifact(name=self.name, path=self.path)

    def as_output(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact specifications for use as an output of a task"""
        return IoArgoprojWorkflowV1alpha1Artifact(name=self.name, path=self.path)

    @property
    def contains_item(self) -> bool:
        """Check whether the artifact contains an argo item reference"""
        item = "{{item"
        if self.path is not None and item in self.path:
            return True
        if self.sub_path is not None and item in self.sub_path:
            return True
        if self.from_task is not None and item in self.from_task:
            return True

        return False


class BucketArtifact(Artifact):
    """This artifact is used to represent a bucket object as an artifact.

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
    Don't use this directly. Use S3InputArtifact or GCSInputArtifact.
    """

    def __init__(self, name: str, path: str, bucket: str, key: str, archive: Optional[Archive] = None) -> None:
        self.bucket = bucket
        self.key = key
        self.archive = archive
        super(BucketArtifact, self).__init__(name, path)


class S3Artifact(BucketArtifact):
    """S3 artifact specification. See `hera.artifact.BucketArtifact`"""

    def as_argument(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact representation for use as an argument to a task"""
        artifact = IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            s3=IoArgoprojWorkflowV1alpha1S3Artifact(bucket=self.bucket, key=self.key),
        )
        if self.archive is not None:
            setattr(artifact, "archive", self.archive.build())
        return artifact

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact representation for use as an input to a task"""
        return self.as_argument()

    def as_output(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact representation for use as an input to a task"""
        return self.as_argument()


class GCSArtifact(BucketArtifact):
    """GCS artifact specification. See `hera.artifact.BucketArtifact`"""

    def as_argument(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact representation for use as an argument to a task"""
        artifact = IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            gcs=IoArgoprojWorkflowV1alpha1GCSArtifact(bucket=self.bucket, key=self.key),
        )
        if self.archive is not None:
            setattr(artifact, "archive", self.archive.build())
        return artifact

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact representation for use as an input to a task"""
        return self.as_argument()

    def as_output(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact representation for use as an input to a task"""
        return self.as_argument()


class GitArtifact(Artifact):
    """Git artifact representation for fetching Git repositories/artifacts as Argo artifacts.

    Parameters
    ----------
    name: str
        Name of the git artifact.
    path: str
        Path to the artifact.
    repo: str
        Name of the repo origin.
    revision: Optional[str] = None
        The revision to fetch e.g. main.
    depth: Optional[int] = None
        The number of commit to fetch during the clone.
    disable_submodules: Optional[bool] = None
        Whether to disable git submodules.
    fetch: Optional[List[str]] = None
        Fetch specifies a number of refs that should be fetched before checkout
    insecure_ignore_host_key: Optional[bool] = None
        Whether to disable SSH strict host key checking during git clone
    username_secret_name: Optional[str] = None,
        The secret name to use to fetch the username.
    username_secret_key: Optional[str] = None
        The key within the username secret to use to fetch the username.
    password_secret_name: Optional[str] = None,
        The secret name to use to fetch the password.
    password_secret_key: Optional[str] = None
        The key within the password secret to use to fetch the password.
    ssh_private_key_secret_name: Optional[str] = None
        The secret name to use to fetch the SSH private key.
    ssh_private_key_secret_key: Optional[str] = None
        The key within the SSH secret to use to fetch the password.
    """

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
        username_secret_name: Optional[str] = None,
        username_secret_key: Optional[str] = None,
        password_secret_name: Optional[str] = None,
        password_secret_key: Optional[str] = None,
        ssh_private_key_secret_name: Optional[str] = None,
        ssh_private_key_secret_key: Optional[str] = None,
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

    def as_argument(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact for use as an argument of a task"""
        git = IoArgoprojWorkflowV1alpha1GitArtifact(repo=self.repo)
        if self.depth is not None:
            setattr(git, "depth", self.depth)

        if self.disable_submodules is not None:
            setattr(git, "disable_submodules", self.disable_submodules)

        if self.fetch is not None:
            setattr(git, "fetch", self.fetch)

        if self.insecure_ignore_host_key is not None:
            setattr(git, "insecure_ignore_host_key", self.insecure_ignore_host_key)

        if self.username_secret_key is not None:
            username_secret = SecretKeySelector(key=self.username_secret_key)
            if self.username_secret_name is not None:
                setattr(username_secret, "name", self.username_secret_name)
            setattr(git, "username_secret", username_secret)

        if self.password_secret_key is not None:
            password_secret = SecretKeySelector(key=self.password_secret_key)
            if self.password_secret_name is not None:
                setattr(password_secret, "name", self.password_secret_name)
            setattr(git, "password_secret", password_secret)

        if self.revision:
            setattr(git, "revision", self.revision)

        if self.ssh_private_key_secret_key is not None:
            ssh_private_key_secret = SecretKeySelector(key=self.ssh_private_key_secret_key)
            if self.ssh_private_key_secret_name is not None:
                setattr(ssh_private_key_secret, "name", self.ssh_private_key_secret_name)
            setattr(git, "ssh_private_key_secret", ssh_private_key_secret)

        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            git=git,
        )

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact for use as an input to a task"""
        return self.as_argument()


class HttpArtifact(Artifact):
    """Representation of an HTTP artifact from an arbitrary origin.

    Parameters
    ----------
    name: str
        Name to assign to the parameter.
    path: str
        Path for storing the parameter content.
    url: str
        URL to fetch the artifact content from.
    """

    def __init__(self, name: str, path: str, url: str) -> None:
        self.url = url
        super(HttpArtifact, self).__init__(name, path)

    def as_argument(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact for use as an argument of a task"""
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            http=IoArgoprojWorkflowV1alpha1HTTPArtifact(url=self.url),
        )

    def as_input(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Assembles the artifact for use as an input to a task"""
        return self.as_argument()
