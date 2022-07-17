from typing import Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GCSArtifact,
    IoArgoprojWorkflowV1alpha1GitArtifact,
    IoArgoprojWorkflowV1alpha1HTTPArtifact,
    IoArgoprojWorkflowV1alpha1S3Artifact,
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
    repo: str
    revision: Optional[str]

    def __init__(self, name: str, path: str, repo: str, revision: str) -> None:
        self.repo = repo
        self.revision = revision
        super(GitArtifact, self).__init__(name, path)

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            git=IoArgoprojWorkflowV1alpha1GitArtifact(repo=self.repo, revision=self.revision),
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
