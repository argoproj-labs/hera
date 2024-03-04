"""The main entrypoint for hera CLI."""

from __future__ import annotations

import importlib.util
import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Generator, Iterable, List

from hera._cli.base import GenerateYaml
from hera.workflows.workflow import Workflow

DEFAULT_EXTENSION = ".yaml"
YAML_EXTENSIONS = {".yml", ".yaml"}


def _write_workflow_to_yaml(target_file: Path, content: str):
    target_file.write_text(content)


def generate_yaml(options: GenerateYaml):
    """Generate yaml from Python Workflow definitions.

    If the provided path is a folder, generates yaml for all Python files containing `Workflow`s
    in that folder
    """
    paths = sorted(expand_paths(options.from_, recursive=options.recursive))

    # Generate a collection of source file paths and their resultant yaml.
    path_to_output: list[tuple[str, str]] = []
    for path in filter_paths(paths, includes=options.include, excludes=options.exclude):
        yaml_outputs = []
        for workflow in load_workflows_from_module(path):
            yaml_outputs.append(workflow.to_yaml())

        if not yaml_outputs:
            continue

        path_to_output.append((path.name, join_workflows(yaml_outputs)))

    # When `to` write file(s) to disk, otherwise output everything to stdout.
    if options.to:
        dest_is_file = options.to.suffix.lower() in YAML_EXTENSIONS

        if dest_is_file:
            os.makedirs(options.to.parent, exist_ok=True)

            output = join_workflows(o for _, o in path_to_output)
            _write_workflow_to_yaml(options.to, output)

        else:
            os.makedirs(options.to, exist_ok=True)

            for dest_path, content in path_to_output:
                _write_workflow_to_yaml((options.to / dest_path).with_suffix(DEFAULT_EXTENSION), content)

    else:
        output = join_workflows(o for _, o in path_to_output)
        sys.stdout.write(output)


def expand_paths(source: Path, recursive: bool = False) -> Generator[Path, None, None]:
    """Expand a `source` path, return the set of python files matching that path.

    Arguments:
        source: The source path to expand. In the event `source` references a
            folder, return all python files in that folder.
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
            if path.suffix == ".py":
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


def load_workflows_from_module(path: Path) -> list[Workflow]:
    """Load the set of `Workflow` objects defined within a given module.

    Arguments:
        path: The path to a given python module

    Returns:
        A list containing all `Workflow` objects defined within that module.
    """
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path, submodule_search_locations=[str(path.parent)])
    assert spec

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    assert spec.loader
    spec.loader.exec_module(module)

    result = []
    for item in module.__dict__.values():
        if isinstance(item, Workflow):
            result.append(item)

    return result


def join_workflows(strings):
    return "\n---\n\n".join(strings)
