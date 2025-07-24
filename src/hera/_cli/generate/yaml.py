from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from hera._cli.base import GenerateYaml
from hera._cli.generate.util import YAML_EXTENSIONS, convert_code, expand_paths, write_output
from hera.workflows._runner.util import create_module_string
from hera.workflows.workflow import Workflow

DEFAULT_EXTENSION = ".yaml"


def generate_yaml(options: GenerateYaml):
    """Generate yaml from Python Workflow definitions.

    If the provided path is a folder, generates yaml for all Python files containing `Workflow`s
    in that folder
    """
    paths = sorted(expand_paths(options.from_, {".py"}, recursive=options.recursive))

    path_to_output = convert_code(
        paths,
        options,
        loader_func=load_workflows_from_module,
        dumper_func=lambda w: w.to_yaml(),
        join_delimiter="---\n",
    )

    write_output(
        options.to,
        path_to_output,
        extensions=YAML_EXTENSIONS,
        default_extension=DEFAULT_EXTENSION,
        join_delimiter="---\n",
    )


def load_workflows_from_module(path: Path) -> list[Workflow]:
    """Load the set of `Workflow` objects defined within a given module.

    Arguments:
        path: The path to a given Python module

    Returns:
        A list containing all `Workflow` objects defined within that module.
    """
    module_name = create_module_string(path)
    spec = importlib.util.spec_from_file_location(module_name, path)
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
