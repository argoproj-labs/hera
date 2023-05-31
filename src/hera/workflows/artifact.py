"""The artifact module provides the base Artifact class, along with the various
types of artifacts as subclasses.

See https://argoproj.github.io/argo-workflows/walk-through/artifacts/
for a tutorial on Artifacts.
"""
from typing import List, Optional, Union, cast

from hera.shared._base_model import BaseModel
from hera.workflows.archive import ArchiveStrategy
from hera.workflows.models import (
    ArchiveStrategy as _ModelArchiveStrategy,
    Artifact as _ModelArtifact,
    ArtifactGC,
    ArtifactoryArtifact as _ModelArtifactoryArtifact,
    ArtifactPaths as _ModelArtifactPaths,
    AzureArtifact as _ModelAzureArtifact,
    GCSArtifact as _ModelGCSArtifact,
    GitArtifact as _ModelGitArtifact,
    HDFSArtifact as _ModelHDFSArtifact,
    HTTPArtifact as _ModelHTTPArtifact,
    OSSArtifact as _ModelOSSArtifact,
    RawArtifact as _ModelRawArtifact,
    S3Artifact as _ModelS3Artifact,
    SecretKeySelector,
)


class Artifact(BaseModel):
    name: str
    archive: Optional[Union[_ModelArchiveStrategy, ArchiveStrategy]] = None
    archive_logs: Optional[bool] = None
    artifact_gc: Optional[ArtifactGC] = None
    deleted: Optional[bool] = None
    from_: Optional[str] = None
    from_expression: Optional[str] = None
    global_name: Optional[str] = None
    mode: Optional[int] = None
    path: Optional[str] = None
    recurse_mode: Optional[str] = None
    sub_path: Optional[str] = None

    def _build_archive(self) -> Optional[_ModelArchiveStrategy]:
        if self.archive is None:
            return None

        if isinstance(self.archive, _ModelArchiveStrategy):
            return self.archive
        return cast(ArchiveStrategy, self.archive)._build_archive_strategy()

    def _build_artifact(self) -> _ModelArtifact:
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
            path=self.path,
            recurse_mode=self.recurse_mode,
            sub_path=self.sub_path,
        )

    def _build_artifact_paths(self) -> _ModelArtifactPaths:
        artifact = self._build_artifact()
        return _ModelArtifactPaths(**artifact.dict())

    def as_name(self, name: str) -> _ModelArtifact:
        artifact = self._build_artifact()
        artifact.name = name
        return artifact


class ArtifactoryArtifact(_ModelArtifactoryArtifact, Artifact):
    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.artifactory = _ModelArtifactoryArtifact(
            url=self.url, password_secret=self.password_secret, username_secret=self.username_secret
        )
        return artifact


class AzureArtifact(_ModelAzureArtifact, Artifact):
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


class GCSArtifact(_ModelGCSArtifact, Artifact):
    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.gcs = _ModelGCSArtifact(
            bucket=self.bucket,
            key=self.key,
            service_account_key_secret=self.service_account_key_secret,
        )
        return artifact


class GitArtifact(_ModelGitArtifact, Artifact):
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


class HDFSArtifact(Artifact):
    # note that `HDFSArtifact` does not inherit from the auto-generated `HDFSArtifact` because there's a
    # conflict in `path` with the base class `Artifact`. Here, we redefine the HDFS `path` to `hdfs_path` to
    # differentiate between the parent class and the child class `path`
    hdfs_path: str
    addresses: Optional[List[str]] = None
    force: Optional[bool] = None
    hdfs_user: Optional[str]
    krb_c_cache_secret: Optional[SecretKeySelector] = None
    krb_config_config_map: Optional[SecretKeySelector] = None
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


class HTTPArtifact(_ModelHTTPArtifact, Artifact):
    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.http = _ModelHTTPArtifact(
            auth=self.auth,
            headers=self.headers,
            url=self.url,
        )
        return artifact


class OSSArtifact(_ModelOSSArtifact, Artifact):
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


class RawArtifact(_ModelRawArtifact, Artifact):
    def _build_artifact(self) -> _ModelArtifact:
        artifact = super()._build_artifact()
        artifact.raw = _ModelRawArtifact(data=self.data)
        return artifact


class S3Artifact(_ModelS3Artifact, Artifact):
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


__all__ = [
    "Artifact",
    *[c.__name__ for c in Artifact.__subclasses__()],
]
