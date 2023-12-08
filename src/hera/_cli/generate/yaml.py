"""The main entrypoint for hera CLI."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Generator

import cappa

from hera._cli.base import GenerateYaml
from hera.workflows.workflow import Workflow


def generate_yaml(options: GenerateYaml):
    """Generate yaml from python Workflow definitions.

    If the provided path is folder, generates yaml for all python files containing `Workflow`s
    in that folder
    """
    paths = sorted(expand_paths(options.from_, recursive=options.recursive))

    # Generate a collection of source file paths and their resultant yaml.
    path_to_output: list[tuple[str, str]] = []
    for path in paths:
        yaml_outputs = []
        for workflow in load_workflows_from_module(path):
            yaml_outputs.append(workflow.to_yaml())

        if not yaml_outputs:
            continue

        yaml_output = "\n---\n".join(yaml_outputs)
        path_to_output.append((path.name, yaml_output))

    # When `to` write file(s) to disk, otherwise output everything to stdout.
    if options.to:
        if options.from_.is_dir():
            if os.path.exists(options.to) and not options.to.is_dir():
                raise cappa.Exit(
                    "The provided source path is a folder, but `--to` points at an existing file.",
                    code=1,
                )

            os.makedirs(options.to, exist_ok=True)

            for path, content in path_to_output:
                full_path = (options.to / path).with_suffix(".yaml")
                full_path.write_text(content)
        else:
            assert len(path_to_output) == 1

            _, content = path_to_output[0]
            options.to.write_text(content)

    else:
        output = "\n---\n".join(o for _, o in path_to_output)
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


def load_workflows_from_module(path: Path) -> list[Workflow]:
    """Load the set of `Workflow` objects defined within a given module.

    Arguments:
        path: The path to a given python module

    Returns:
        A list containing all `Workflow` objects defined within that module.
    """
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec

    module = importlib.util.module_from_spec(spec)

    assert spec.loader
    spec.loader.exec_module(module)

    result = []
    for item in module.__dict__.values():
        if isinstance(item, Workflow):
            result.append(item)

    return result
