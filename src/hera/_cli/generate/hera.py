import os
import sys
from collections import ChainMap
from pathlib import Path
from typing import Any, Generator, Iterable, List, Optional, Tuple, get_args

import yaml

from hera._cli.base import GeneratePython
from hera._cli.generate.util import YAML_EXTENSIONS, expand_paths, filter_paths
from hera.shared._pydantic import BaseModel
from hera.shared._type_util import get_annotated_metadata, is_optionally_subtype, unwrap_annotation
from hera.workflows._meta_mixins import ModelMapperMixin, _get_model_attr
from hera.workflows.models import (
    Template,
    Workflow as _ModelWorkflow,
)
from hera.workflows.workflow import Workflow

try:
    from inspect import get_annotations  # type: ignore
except ImportError:
    from hera.shared._inspect import get_annotations  # type: ignore

DEFAULT_EXTENSION = ".py"


def generate_workflow(options: GeneratePython) -> str:
    """Generate python from yaml Workflow definitions.

    If the provided path is a folder, generates python for all yaml files containing `Workflow`s
    in that folder
    """
    paths = sorted(expand_paths(options.from_, YAML_EXTENSIONS, recursive=options.recursive))

    # Generate a collection of source file paths and their resultant python.
    path_to_output: list[tuple[str, str]] = []
    for path in filter_paths(paths, includes=options.include, excludes=options.exclude):
        python_outputs = []
        for workflow in load_yaml_workflows(path):
            python_outputs.append(workflow_to_python(workflow))

        if not python_outputs:
            continue

        path_to_output.append((path.name, join_workflows(python_outputs)))

    # When `to` write file(s) to disk, otherwise output everything to stdout.
    if options.to:
        dest_is_file = options.to.suffix.lower() == ".py"

        if dest_is_file:
            os.makedirs(options.to.parent, exist_ok=True)

            output = join_workflows(o for _, o in path_to_output)
            options.to.write_text(output)

        else:
            os.makedirs(options.to, exist_ok=True)

            for dest_path, content in path_to_output:
                dest = (options.to / dest_path).with_suffix(DEFAULT_EXTENSION)
                dest.write_text(content)

    else:
        output = join_workflows(o for _, o in path_to_output)
        sys.stdout.write(output)


def load_yaml_workflows(path: Path) -> Generator[_ModelWorkflow, None, None]:
    """Load the YAML file containing a Workflow(s)."""
    for yaml_workflow in yaml.safe_load_all(path.read_text()):
        if isinstance(yaml_workflow, dict):
            yield _ModelWorkflow.parse_obj(yaml_workflow)
        else:
            raise ValueError(f"Invalid YAML workflow: {yaml_workflow}")


def is_basic_type(annotation: type) -> bool:
    """Check if the annotation is a basic JSON type."""
    return is_optionally_subtype(annotation, (str, int, float, bool))


def json_to_python(value: Any, annotation: Optional[type] = None) -> Tuple[str, List[str]]:
    """Convert a JSON value to a Python representation."""
    if annotation is not None and is_basic_type(annotation) or isinstance(value, (str, int, float, bool)):
        return f'"{str(value).strip()}"', []
    elif annotation is not None and is_optionally_subtype(annotation, list) or isinstance(value, list):
        python_repr = []
        imports = []
        for v in value:
            to_python, sub_imports = json_to_python(v)
            python_repr.append(to_python)
            imports.extend(sub_imports)
        return "[" + ",".join(python_repr) + "]", imports
    elif annotation is not None and is_optionally_subtype(annotation, dict) or isinstance(value, dict):
        python_repr = []
        imports = []
        for k, v in value.items():
            to_python, sub_imports = json_to_python(v)
            python_repr.append(f'"{k}": {to_python}')
            imports.extend(sub_imports)
        return "{" + ",".join(python_repr) + "}", imports
    elif annotation is not None and is_optionally_subtype(annotation, BaseModel) or isinstance(value, BaseModel):
        return model_to_python(value)
    else:
        raise ValueError(f"Unsupported type: {annotation} for value {value}")


def container_to_python(model: Template) -> Tuple[str, List[str]]:
    return (
        f"""\
Container(
    name="{model.name}",
    image="{model.container.image}",
    command={model.container.command},
    args={model.container.args},
)
""",
        [],
    )


def model_to_python(model: BaseModel) -> Tuple[str, List[str]]:
    model_name = model.__class__.__name__
    if model_name == "Template":
        return container_to_python(model)

    model_imports = [model_name]
    class_def = [f"{model_name}("]
    for attr in ChainMap(*(get_annotations(c) for c in model.__class__.__mro__)):
        if attr == "__slots__" or getattr(model, attr) is None:
            continue
        value = getattr(model, attr)
        assign_value, sub_model_imports = json_to_python(value, type(value))
        model_imports.extend(sub_model_imports)

        class_def.append(f"{attr}={assign_value},")
    class_def.append(")")
    return "\n".join(class_def), model_imports


def workflow_to_python(model: _ModelWorkflow) -> str:
    hera_imports = ["Workflow"]
    model_imports = []
    class_def = ["with Workflow("]
    context_def = []
    for attr, annotation in Workflow._get_all_annotations().items():
        if mappers := get_annotated_metadata(annotation, ModelMapperMixin.ModelMapper):
            if len(mappers) != 1:
                raise ValueError("Expected only one model mapper")
            if mappers[0].model_path:
                value = _get_model_attr(model, mappers[0].model_path)
                if value is not None:
                    if attr == "templates":
                        for template in value:
                            t, sub_model_imports = json_to_python(template, get_args(unwrap_annotation(annotation)))
                            hera_imports.append("Container")
                            model_imports.extend(sub_model_imports)
                            context_def.append("    " + t)
                    else:
                        value, sub_model_imports = json_to_python(value, unwrap_annotation(annotation))
                        model_imports.extend(sub_model_imports)
                        class_def.append(f"{attr}={value},")

    imports = list(map(lambda x: f"from hera.workflows import {x}", hera_imports))
    imports.extend(map(lambda x: f"from hera.workflows.models import {x}", model_imports))

    return "\n".join(imports + class_def + [") as w:"] + context_def)


def join_workflows(workflows: Iterable[str]) -> str:
    """Join a collection of workflows into a single string."""
    return "\n".join(workflows)
