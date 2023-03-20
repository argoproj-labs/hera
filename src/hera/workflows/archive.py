from typing import Optional

from hera.shared._base_model import BaseModel
from hera.workflows.models import (
    ArchiveStrategy as _ModelArchiveStrategy,
    NoneStrategy as _ModelNoneStrategy,
    TarStrategy as _ModelTarStrategy,
    ZipStrategy as _ModelZipStrategy,
)


class ArchiveStrategy(BaseModel):
    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy()


class NoneArchiveStrategy(ArchiveStrategy):
    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy(none=_ModelNoneStrategy())


class TarArchiveStrategy(ArchiveStrategy):
    compression_level: Optional[int] = None

    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy(tar=_ModelTarStrategy(compression_level=self.compression_level))


class ZipArchiveStrategy(ArchiveStrategy):
    def _build_archive_strategy(self) -> _ModelArchiveStrategy:
        return _ModelArchiveStrategy(zip=_ModelZipStrategy())


__all__ = [
    "ArchiveStrategy",
    *[c.__name__ for c in ArchiveStrategy.__subclasses__()],
]
