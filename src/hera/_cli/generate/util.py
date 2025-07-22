import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Set, Union

from hera._cli.base import GeneratePython, GenerateYaml

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


def convert_code(
    paths: List[Path],
    options: Union[GenerateYaml, GeneratePython],
    loader_func: Callable[[Path], Any],
    dumper_func: Callable[[Any], str],
    join_delimiter: str,
) -> Dict[str, str]:
    """Convert inputs list of workflows into a dict of output paths to their output text."""
    path_to_output: dict[str, str] = {}
    for path in filter_paths(paths, includes=options.include, excludes=options.exclude):
        outputs = []
        for workflow in loader_func(path):
            outputs.append(dumper_func(workflow))

        if not outputs:
            continue

        if options.recursive:
            if options.flatten:
                if path.name in path_to_output:
                    path_to_output[path.name] = join_delimiter.join([path_to_output[path.name]] + outputs)
                else:
                    path_to_output[path.name] = join_delimiter.join(outputs)
            else:
                path_to_output[str(path.relative_to(options.from_))] = join_delimiter.join(outputs)
        else:
            path_to_output[path.name] = join_delimiter.join(outputs)
    return path_to_output
