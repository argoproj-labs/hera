import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Optional, Set

YAML_EXTENSIONS = {".yml", ".yaml"}


def expand_paths(source: Path, suffixes: Set[str], recursive: bool = False) -> Generator[Path, None, None]:
    """Expand a `source` path, return the set of files with any of the given suffixes matching that path.

    Arguments:
        source: The source path to expand. In the event `source` references a
            folder, return all files with any of the suffixes in that folder.
        suffixes: The set of suffixes to match against the files in the `source` path.
        recursive: If True, recursively traverse the `source` path.
    """
    if not source.is_dir():
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


def write_output(
    output_path: Optional[Path],
    input_paths_to_output: Dict[str, str],
    extensions: Set[str],
    default_extension: str,
    join_delimiter: str,
) -> None:
    if not output_path:
        output = join_delimiter.join(input_paths_to_output.values())
        sys.stdout.write(output)
        return

    dest_is_file = output_path.suffix.lower() in extensions or output_path.exists() and output_path.is_file()

    if dest_is_file:
        output_path.parent.mkdir(exist_ok=True)

        output = join_delimiter.join(input_paths_to_output.values())
        output_path.write_text(output)
    else:
        output_path.mkdir(exist_ok=True)

        for dest_path, content in input_paths_to_output.items():
            dest = (output_path / dest_path).with_suffix(default_extension)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content)
