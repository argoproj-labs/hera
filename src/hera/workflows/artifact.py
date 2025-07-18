"""The `hera.workflows.artifact` module provides the base Artifact class, along with the various types of artifacts as subclasses.

Tip:
    [Read the Hera walk-through for Artifacts.](../../../walk-through/artifacts.md)
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable, List, Optional, Union, cast

from hera.shared._pydantic import BaseModel
from hera.workflows.archive import ArchiveStrategy
from hera.workflows.models import (
    ArchiveStrategy as _ModelArchiveStrategy,
    Artifact as _ModelArtifact,
    ArtifactGC,
    ArtifactoryArtifact as _ModelArtifactoryArtifact,
    ArtifactPaths as _ModelArtifactPaths,
    AzureArtifact as _ModelAzureArtifact,
    ConfigMapKeySelector,
    GCSArtifact as _ModelGCSArtifact,
    GitArtifact as _ModelGitArtifact,
    HDFSArtifact as _ModelHDFSArtifact,
    HTTPArtifact as _ModelHTTPArtifact,
    OSSArtifact as _ModelOSSArtifact,
    RawArtifact as _ModelRawArtifact,
    S3Artifact as _ModelS3Artifact,
    SecretKeySelector,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.WARNING)

_DEFAULT_ARTIFACT_INPUT_DIRECTORY = "/tmp/hera-inputs/artifacts/"


class ArtifactLoader(Enum):
    """Enum for artifact loader options."""

    json = "json"
    """Deserialize the JSON-string Artifact file to a Python object (the target variable can be any JSON-compatible type)."""

    file = "file"
    """Read the contents of the Artifact file directly as a string (the target variable must be a `str` type)."""


class Artifact(BaseModel):
    """Base artifact representation."""

    name: Optional[str] = None
    """name of the artifact"""

    archive: Optional[Union[_ModelArchiveStrategy, ArchiveStrategy]] = None
    """artifact archiving configuration"""

    archive_logs: Optional[bool] = None
    """whether to log the archive object"""

    artifact_gc: Optional[ArtifactGC] = None
    """artifact garbage collection configuration"""

    deleted: Optional[bool] = None
    """whether the artifact is deleted"""

    from_: Optional[str] = None
    """configures the artifact task/step origin"""

    from_expression: Optional[str] = None
    """an expression that dictates where to obtain the artifact from"""

    global_name: Optional[str] = None
    """global workflow artifact name"""

    mode: Optional[int] = None
    """mode bits to use on the artifact, must be a value between 0 and 0777 set when loading input artifacts."""

    path: Optional[str] = None
    """path where the artifact should be placed/loaded from"""

    recurse_mode: Optional[bool] = None
    """recursion mode when applying the permissions of the artifact if it is an artifact folder"""

    sub_path: Optional[str] = None
    """allows the specification of an artifact from a subpath within the main source."""

    loader: Optional[ArtifactLoader] = None
    """used for input Artifact annotations for determining how to load the data.

    Note: A loader value of 'None' must be used with an underlying type of 'str' or Path-like class."""

    loadb: Optional[Callable[[bytes], Any]] = None
    """used to specify a loader function to deserialise from bytes for Annotated Artifact function parameters"""

    dumpb: Optional[Callable[[Any], bytes]] = None
    """used to specify a dumper function to serialise the Artifact value as bytes for Annotated Artifact function parameters"""

    loads: Optional[Callable[[str], Any]] = None
    """used to specify a loader function to deserialise a string representation of an object for Annotated Artifact function parameters"""

    dumps: Optional[Callable[[Any], str]] = None
    """used to specify a dumper function to serialise the Artifact value as a string for Annotated Artifact function parameters"""

    optional: Optional[bool] = None
    """whether the Artifact is optional. For an input Artifact, this means it may possibly not
    exist at the specified path during the template's runtime. For an output Artifact, it may
    possibly not be generated during the step/task and available as an output to subsequent steps/tasks."""

    output: bool = False
    """used to specify artifact as an output in function signature annotations"""

    def _check_name(self):
        if not self.name:
            raise ValueError("name cannot be `None` or empty when used")

    def _get_default_inputs_path(self) -> str:
        return _DEFAULT_ARTIFACT_INPUT_DIRECTORY + f"{self.name}"

    def _build_archive(self) -> Optional[_ModelArchiveStrategy]:
        if self.archive is None:
            return None

        if isinstance(self.archive, _ModelArchiveStrategy):
            return self.archive
        return cast(ArchiveStrategy, self.archive)._build_archive_strategy()

    def _build_artifact(self) -> _ModelArtifact:
        self._check_name()
        assert self.name
        return _ModelArtifact(
            name=self.name,
            archive=self._build_archive(),
            archive_logs=self.archive_logs,
            artifact_gc=self.artifact_gc,
            deleted=self.deleted,
            from_=self.from_,
            from_expression=self.from_expression,
            global_name=self.global_name,
            mode=self.mode,
            optional=self.optional,
            path=self.path,
            recurse_mode=self.recurse_mode,
            sub_path=self.sub_path,
        )

    def _build_artifact_paths(self) -> _ModelArtifactPaths:
        self._check_name()
        artifact = self._build_artifact()
        return _ModelArtifactPaths(**artifact.dict())

    def as_name(self, name: str) -> _ModelArtifact:
        """Returns a 'built' copy of the current artifact, renamed using the specified `name`.

        Warning: DEPRECATED
            use with_name.
        """
        _logger.warning("'as_name' is deprecated, use 'with_name'")
        artifact = self._build_artifact()
        artifact.name = name
        return artifact

    def with_name(self, name: str) -> Artifact:
        """Returns a copy of the current artifact, renamed using the specified `name`."""
        artifact = self.copy(deep=True)
        artifact.name = name
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return [
            "mode",
            "name",
            "optional",
            "path",
            "recurseMode",
            "subPath",
        ]


class ArtifactoryArtifact(_ModelArtifactoryArtifact, Artifact):
    """An artifact sourced from Artifactory."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.artifactory = _ModelArtifactoryArtifact(
            url=self.url, password_secret=self.password_secret, username_secret=self.username_secret
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + ["url", "password_secret", "username_secret"]


class AzureArtifact(_ModelAzureArtifact, Artifact):
    """An artifact sourced from Microsoft Azure."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.azure = _ModelAzureArtifact(
            account_key_secret=self.account_key_secret,
            blob=self.blob,
            container=self.container,
            endpoint=self.endpoint,
            use_sdk_creds=self.use_sdk_creds,
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + [
            "endpoint",
            "container",
            "blob",
            "account_key_secret",
            "use_sdk_creds",
        ]


class GCSArtifact(_ModelGCSArtifact, Artifact):
    """An artifact sourced from Google Cloud Storage."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.gcs = _ModelGCSArtifact(
            bucket=self.bucket,
            key=self.key,
            service_account_key_secret=self.service_account_key_secret,
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + ["bucket", "key", "service_account_key_secret"]


class GitArtifact(_ModelGitArtifact, Artifact):
    """An artifact sourced from GitHub."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.git = _ModelGitArtifact(
            branch=self.branch,
            depth=self.depth,
            disable_submodules=self.disable_submodules,
            fetch=self.fetch,
            insecure_ignore_host_key=self.insecure_ignore_host_key,
            password_secret=self.password_secret,
            repo=self.repo,
            revision=self.revision,
            single_branch=self.single_branch,
            ssh_private_key_secret=self.ssh_private_key_secret,
            username_secret=self.username_secret,
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + [
            "branch",
            "depth",
            "disable_submodules",
            "fetch",
            "insecure_ignore_host_key",
            "password_secret",
            "repo",
            "revision",
            "single_branch",
            "ssh_private_key_secret",
            "username_secret",
        ]


class HDFSArtifact(Artifact):
    """A Hadoop File System artifact.

    Note that `HDFSArtifact` does not inherit from the auto-generated `HDFSArtifact` because there's a
    conflict in `path` with the base class `Artifact`. Here, we redefine the HDFS `path` to `hdfs_path` to
    differentiate between the parent class and the child class `path`.
    """

    hdfs_path: str
    addresses: Optional[List[str]] = None
    force: Optional[bool] = None
    hdfs_user: Optional[str]
    krb_c_cache_secret: Optional[SecretKeySelector] = None
    krb_config_config_map: Optional[ConfigMapKeySelector] = None
    krb_keytab_secret: Optional[SecretKeySelector] = None
    krb_realm: Optional[str] = None
    krb_service_principal_name: Optional[str] = None
    krb_username: Optional[str] = None

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.hdfs = _ModelHDFSArtifact(
            addresses=self.addresses,
            force=self.force,
            hdfs_user=self.hdfs_user,
            krb_c_cache_secret=self.krb_c_cache_secret,
            krb_config_config_map=self.krb_config_config_map,
            krb_keytab_secret=self.krb_keytab_secret,
            krb_realm=self.krb_realm,
            krb_service_principal_name=self.krb_service_principal_name,
            krb_username=self.krb_username,
            path=self.hdfs_path,
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + [
            "addresses",
            "force",
            "hdfs_path",
            "hdfs_user",
            "krb_c_cache_secret",
            "krb_config_config_map",
            "krb_keytab_secret",
            "krb_realm",
            "krb_service_principal_name",
            "krb_username",
        ]


class HTTPArtifact(_ModelHTTPArtifact, Artifact):
    """An artifact sourced from an HTTP URL."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.http = _ModelHTTPArtifact(
            auth=self.auth,
            headers=self.headers,
            url=self.url,
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + ["auth", "headers", "url"]


class OSSArtifact(_ModelOSSArtifact, Artifact):
    """An artifact sourced from OSS."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.oss = _ModelOSSArtifact(
            access_key_secret=self.access_key_secret,
            bucket=self.bucket,
            create_bucket_if_not_present=self.create_bucket_if_not_present,
            endpoint=self.endpoint,
            key=self.key,
            lifecycle_rule=self.lifecycle_rule,
            secret_key_secret=self.secret_key_secret,
            security_token=self.security_token,
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + [
            "access_key_secret",
            "bucket",
            "create_bucket_if_not_present",
            "endpoint",
            "key",
            "lifecycle_rule",
            "secret_key_secret",
            "security_token",
        ]


class RawArtifact(_ModelRawArtifact, Artifact):
    """A raw bytes artifact representation."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.raw = _ModelRawArtifact(data=self.data)
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + ["data"]


class S3Artifact(_ModelS3Artifact, Artifact):
    """An artifact sourced from AWS S3."""

    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.s3 = _ModelS3Artifact(
            access_key_secret=self.access_key_secret,
            bucket=self.bucket,
            create_bucket_if_not_present=self.create_bucket_if_not_present,
            encryption_options=self.encryption_options,
            endpoint=self.endpoint,
            insecure=self.insecure,
            key=self.key,
            region=self.region,
            role_arn=self.role_arn,
            secret_key_secret=self.secret_key_secret,
            use_sdk_creds=self.use_sdk_creds,
        )
        return artifact

    @classmethod
    def _get_input_attributes(cls):
        """Return the attributes used for input artifact annotations."""
        return super()._get_input_attributes() + [
            "access_key_secret",
            "bucket",
            "create_bucket_if_not_present",
            "encryption_options",
            "endpoint",
            "insecure",
            "key",
            "region",
            "role_arn",
            "secret_key_secret",
            "use_sdk_creds",
        ]


__all__ = [
    "Artifact",
    *[c.__name__ for c in Artifact.__subclasses__()],
    "ArtifactLoader",
]
