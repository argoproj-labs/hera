"""The main entrypoint for hera CLI."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Iterable

from hera._cli.base import GenerateYaml
from hera._cli.generate.util import YAML_EXTENSIONS, expand_paths, filter_paths
from hera.workflows.workflow import Workflow

DEFAULT_EXTENSION = ".yaml"


def _write_workflow_to_yaml(target_file: Path, content: str):
    target_file.write_text(content)


def generate_yaml(options: GenerateYaml):
    """Generate yaml from Python Workflow definitions.

    If the provided path is a folder, generates yaml for all Python files containing `Workflow`s
    in that folder
    """
    paths = sorted(expand_paths(options.from_, {".py"}, recursive=options.recursive))

    # Generate a collection of source file paths and their resultant yaml.
    path_to_output: list[tuple[str, str]] = []
    for path in filter_paths(paths, includes=options.include, excludes=options.exclude):
        yaml_outputs = []
        for workflow in load_workflows_from_module(path):
            yaml_outputs.append(workflow.to_yaml())

        if not yaml_outputs:
            continue

        path_to_output.append((path.name, join_yaml_strings(yaml_outputs)))

    # When `to` write file(s) to disk, otherwise output everything to stdout.
    if options.to and isinstance(options.to, Path):
        dest_is_file = options.to.suffix.lower() in YAML_EXTENSIONS

        if dest_is_file:
            os.makedirs(options.to.parent, exist_ok=True)

            output = join_yaml_strings(o for _, o in path_to_output)
            options.to.write_text(output)

        else:
            os.makedirs(options.to, exist_ok=True)

            for dest_path, content in path_to_output:
                dest = (options.to / dest_path).with_suffix(DEFAULT_EXTENSION)
                dest.write_text(content)

    else:
        output = join_yaml_strings(o for _, o in path_to_output)
        sys.stdout.write(output)


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


def join_yaml_strings(strings: Iterable[str]) -> str:
    return "\n---\n\n".join(strings)
