"""The `hera.workflows.archive` module provides archival behavior strategies for artifacts."""

from dataclasses import dataclass
from typing import Optional

from hera.workflows.models import (
    ArchiveStrategy as _ModelArchiveStrategy,
    NoneStrategy as _ModelNoneStrategy,
    TarStrategy as _ModelTarStrategy,
    ZipStrategy as _ModelZipStrategy,
)


@dataclass(kw_only=True)
class ArchiveStrategy:
    """Base archive strategy model."""

    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy()


@dataclass(kw_only=True)
class NoneArchiveStrategy(ArchiveStrategy):
    """`NoneArchiveStrategy` indicates artifacts should skip serialization."""

    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy(none=_ModelNoneStrategy())


@dataclass(kw_only=True)
class TarArchiveStrategy(ArchiveStrategy):
    """`TarArchiveStrategy` indicates artifacts should be serialized using the `tar` strategy.

    Tar archiving is performed using the specified compression level.
    """

    compression_level: Optional[int] = None

    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy(tar=_ModelTarStrategy(compression_level=self.compression_level))


@dataclass(kw_only=True)
class ZipArchiveStrategy(ArchiveStrategy):
    """`ZipArchiveStrategy` indicates artifacts should be serialized using the `zip` strategy."""

    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy(zip=_ModelZipStrategy())


__all__ = [
    "ArchiveStrategy",
    *[c.__name__ for c in ArchiveStrategy.__subclasses__()],
]
