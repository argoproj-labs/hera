from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Artifact,
    IoArgoprojWorkflowV1alpha1GCSArtifact,
    IoArgoprojWorkflowV1alpha1S3Artifact,
)
from pydantic import BaseModel


class Artifact(BaseModel):
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

    name: str
    path: str

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Constructs the corresponding Argo artifact representation"""
        return IoArgoprojWorkflowV1alpha1Artifact(name=self.name, path=self.path)

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Constructs the corresponding Argo artifact inputs representation"""
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

    from_task: str
    artifact_name: str

    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Constructs the corresponding Argo artifact representation"""
        _from = f"{{{{tasks.{self.from_task}.outputs.artifacts.{self.artifact_name}}}}}"
        return IoArgoprojWorkflowV1alpha1Artifact(name=self.name, path=self.path, _from=_from)


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
    key: str
        Key of the artifact in the bucket.

    Notes
    -----
    Don't use this directly. Use S3InputArtifact or GCSInputArtifact
    """

    key: str


class S3Artifact(BucketArtifact):
    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            s3=IoArgoprojWorkflowV1alpha1S3Artifact(key=self.key),
        )

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Constructs the corresponding Argo artifact inputs representation"""
        return self.get_spec()


class GCSArtifact(BucketArtifact):
    def get_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        return IoArgoprojWorkflowV1alpha1Artifact(
            name=self.name,
            path=self.path,
            gcs=IoArgoprojWorkflowV1alpha1GCSArtifact(key=self.key),
        )

    def get_input_spec(self) -> IoArgoprojWorkflowV1alpha1Artifact:
        """Constructs the corresponding Argo artifact inputs representation"""
        return self.get_spec()
