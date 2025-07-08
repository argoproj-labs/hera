import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Generator, Iterable, List, Set

YAML_EXTENSIONS = {".yml", ".yaml"}


def expand_paths(source: Path, suffixes: Set[str], recursive: bool = False) -> Generator[Path, None, None]:
    """Expand a `source` path, return the set of files with any of the given suffixes matching that path.

    Arguments:
        source: The source path to expand. In the event `source` references a
            folder, return all python files in that folder.
        suffixes: The set of suffixes to match against the files in the `source` path.
        recursive: If True, recursively traverse the `source` path.
    """
    source_is_dir = source.is_dir()
    if not source_is_dir:
        yield source
        return

    iterator = os.walk(source) if recursive else ((next(os.walk(source))),)

    for dir, _, file_names in iterator:
        for file_name in file_names:
            path = Path(os.path.join(dir, file_name))
            if path.suffix in suffixes:
                yield path


def filter_paths(
    paths: List[Path],
    includes: List[str],
    excludes: List[str],
) -> Iterable[Path]:
    for path in paths:
        raw_path = str(path)
        if includes:
            any_includes_match = any(fnmatch(raw_path, include) for include in includes)
            if not any_includes_match:
                continue

        if excludes:
            any_excludes_match = any(fnmatch(raw_path, exclude) for exclude in excludes)
            if any_excludes_match:
                continue

        yield path
