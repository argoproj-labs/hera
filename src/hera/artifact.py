from typing import Optional

from hera.models import Artifact as _ModelArtifact


class Artifact(_ModelArtifact):
    def as_name(self, name: str):
        """Changes the name of the artifact."""
        self.name = name
        return self

    def to_path(self, path: str, sub_path: Optional[str] = None):
        """Change the paths of the artifact"""
        self.path = path
        self.sub_path = sub_path
        return self

    @property
    def contains_item(self) -> bool:
        """Check whether the artifact contains an argo item reference"""
        item = "{{item"
        if self.path is not None and item in self.path:
            return True
        if self.sub_path is not None and item in self.sub_path:
            return True
        if self.from_ is not None and item in self.from_:
            return True

        return False


__all__ = ["Artifact"]
