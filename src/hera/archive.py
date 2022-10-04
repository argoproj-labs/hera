from dataclasses import dataclass
from typing import Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1ArchiveStrategy,
    IoArgoprojWorkflowV1alpha1TarStrategy,
)


@dataclass
class Archive:
    """Archive sets the archival behavior of artifacts.

    Attributes
    ----------
    disable_compression: Optional[bool] = None
        Whether to disable compression intentionally.
    tar_compression_level: Optional[int]
        Specifies the gzip compression level to use for an artifact. The default is the gzip `flate.DefaultCompression`
        which is set to -1.
    zip: Optional[bool] = None
        Whether to unzip zipped input artifacts.
    """

    disable_compression: Optional[bool] = None
    tar_compression_level: Optional[int] = None
    zip: Optional[bool] = None

    def build(self) -> IoArgoprojWorkflowV1alpha1ArchiveStrategy:
        strategy = IoArgoprojWorkflowV1alpha1ArchiveStrategy()
        if self.disable_compression is not None and self.disable_compression:
            # this needs to be set only in the `True` case as `False` is also interpreted as `disable archiving`
            setattr(strategy, "none", {})
        if self.tar_compression_level is not None:
            setattr(
                strategy, "tar", IoArgoprojWorkflowV1alpha1TarStrategy(compression_level=self.tar_compression_level)
            )
        if self.zip is not None and self.zip:
            # this needs to be set only in the `True` case as `False` is also interpreted as `disable archiving`
            setattr(strategy, "zip", self.zip)
        return strategy
