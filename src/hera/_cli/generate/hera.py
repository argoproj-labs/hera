import os
import sys
from collections import ChainMap
from dataclasses import (
    dataclass,
    field as dc_field,
)
from pathlib import Path
from typing import Any, Generator, Iterable, List, Optional, Tuple, Type, Union, cast, get_args

import yaml

from hera._cli.base import GeneratePython
from hera._cli.generate.util import YAML_EXTENSIONS, expand_paths, filter_paths
from hera.shared._pydantic import BaseModel
from hera.shared._type_util import get_annotated_metadata, is_optionally_subtype, unwrap_annotation
from hera.workflows._meta_mixins import ModelMapperMixin, _get_model_attr
from hera.workflows.cluster_workflow_template import ClusterWorkflowTemplate
from hera.workflows.container import Container
from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.cron_workflow import CronWorkflow
from hera.workflows.dag import DAG
from hera.workflows.data import Data
from hera.workflows.http_template import HTTP
from hera.workflows.models import (
    ClusterWorkflowTemplate as _ModelClusterWorkflowTemplate,
    CronWorkflow as _ModelCronWorkflow,
    Metadata,
    Template,
    Workflow as _ModelWorkflow,
    WorkflowTemplate as _ModelWorkflowTemplate,
)
from hera.workflows.resource import Resource
from hera.workflows.script import Script
from hera.workflows.steps import Step, Steps
from hera.workflows.suspend import Suspend
from hera.workflows.task import Task
from hera.workflows.workflow import Workflow
from hera.workflows.workflow_template import WorkflowTemplate

try:
    from inspect import get_annotations  # type: ignore
except ImportError:
    from hera.shared._inspect import get_annotations  # type: ignore

DEFAULT_EXTENSION = ".py"

ModelWorkflow = Union[
    _ModelWorkflow,
    _ModelWorkflowTemplate,
    _ModelClusterWorkflowTemplate,
    _ModelCronWorkflow,
]


@dataclass
class FileBuilder:
    hera_imports: list[str] = dc_field(default_factory=list)
    model_imports: list[str] = dc_field(default_factory=list)
    class_def: list[str] = dc_field(default_factory=list)
    context_def: list[str] = dc_field(default_factory=list)


def generate_workflow(options: GeneratePython):
    """Generate Python (Hera) Workflow definitions from YAML definitions.

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


def load_yaml_workflows(path: Path) -> Generator[ModelWorkflow, None, None]:
    """Load the YAML file containing a Workflow(s)."""
    for yaml_workflow in yaml.safe_load_all(path.read_text()):
        if isinstance(yaml_workflow, dict):
            if yaml_workflow["kind"] == "Workflow":
                yield _ModelWorkflow.parse_obj(yaml_workflow)
            elif yaml_workflow["kind"] == "WorkflowTemplate":
                yield _ModelWorkflowTemplate.parse_obj(yaml_workflow)
            elif yaml_workflow["kind"] == "ClusterWorkflowTemplate":
                yield _ModelClusterWorkflowTemplate.parse_obj(yaml_workflow)
            elif yaml_workflow["kind"] == "CronWorkflow":
                yield _ModelCronWorkflow.parse_obj(yaml_workflow)
            else:
                raise ValueError(f"Unrecognised Workflow kind: {yaml_workflow['kind']}")
        else:
            raise ValueError(f"Invalid YAML workflow: {yaml_workflow}")


def is_basic_type(annotation: type) -> bool:
    """Check if the annotation is a basic JSON type."""
    return is_optionally_subtype(annotation, (str, int, float, bool))


def python_obj_to_repr(value: Any, annotation: Optional[type] = None) -> Tuple[str, List[str], List[str]]:
    """Convert a JSON value to a Python string representation, without "None" values.

    This function also collects the assumed Hera/model imports and returns them.
    """
    if annotation is not None and is_basic_type(annotation) or isinstance(value, (str, int, float, bool)):
        return repr(value), [], []
    elif annotation is not None and is_optionally_subtype(annotation, list) or isinstance(value, list):
        python_repr = []
        model_imports = []
        hera_imports = []
        for v in value:
            to_python, sub_hera_imports, sub_imports = python_obj_to_repr(v)
            python_repr.append(to_python)
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_imports)
        return "[" + ", ".join(python_repr) + "]", hera_imports, model_imports
    elif annotation is not None and is_optionally_subtype(annotation, dict) or isinstance(value, dict):
        python_repr = []
        model_imports = []
        hera_imports = []
        for k, v in value.items():
            to_python, sub_hera_imports, sub_imports = python_obj_to_repr(v)
            python_repr.append(f"{repr(k)}: {to_python}")
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_imports)
        return "{" + ", ".join(python_repr) + "}", hera_imports, model_imports
    elif annotation is not None and is_optionally_subtype(annotation, BaseModel) or isinstance(value, BaseModel):
        return model_to_python(value)
    else:
        raise ValueError(f"Unsupported type: {annotation} for value {value}")


def convert_to_hera_template(
    template: Template,
    template_type_field: BaseModel,
    hera_template_class: Type[BaseModel],
) -> Tuple[str, List[str], List[str]]:
    hera_imports = [hera_template_class.__name__]
    model_imports = []

    template_keys = set(hera_template_class.__fields__.keys()).intersection(template.__fields__.keys())
    template_type_field_keys = set(hera_template_class.__fields__.keys()).intersection(
        template_type_field.__fields__.keys()
    )

    hera_template_str = [f"{hera_template_class.__name__}("]
    for field in template.__fields__:
        # Special case for http which shouldn't be a field in template_keys (but is)
        if field in template_keys and getattr(template, field) is not None and field != "http":
            val, sub_hera_imports, sub_model_imports = python_obj_to_repr(getattr(template, field))
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_model_imports)
            hera_template_str.append(f"{field}={val},")

        if field == "metadata" and getattr(template, field) is not None:
            metadata = cast(Metadata, getattr(template, field))
            if metadata.labels:
                # these are simple str to str dicts, so nothing to import
                labels, _, _ = python_obj_to_repr(metadata.labels)
                hera_template_str.append(f"labels={labels},")

            if metadata.annotations:
                # these are simple str to str dicts, so nothing to import
                annotations, _, _ = python_obj_to_repr(metadata.annotations)
                hera_template_str.append(f"annotations={annotations},")

    for field in template_type_field.__fields__:
        if field in template_type_field_keys and getattr(template_type_field, field) is not None:
            val, sub_hera_imports, sub_model_imports = python_obj_to_repr(getattr(template_type_field, field))
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_model_imports)
            hera_template_str.append(f"{field}={val},")

    hera_template_str.append(")")

    return (
        "\n".join(hera_template_str),
        hera_imports,
        model_imports,
    )


def convert_to_hera_equivalent(
    model_class_obj: BaseModel,
    hera_class: Type[BaseModel],
) -> Tuple[str, List[str], List[str]]:
    hera_imports = [hera_class.__name__]
    model_imports = []

    template_keys = set(model_class_obj.__fields__.keys()).intersection(hera_class.__fields__.keys())

    hera_template_str = [f"{hera_class.__name__}("]
    for field in hera_class.__fields__:
        if field in template_keys and getattr(model_class_obj, field) is not None:
            val, sub_hera_imports, sub_model_imports = python_obj_to_repr(getattr(model_class_obj, field))
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_model_imports)
            hera_template_str.append(f"{field}={val},")

    hera_template_str.append(")")
    return (
        "\n".join(hera_template_str),
        hera_imports,
        model_imports,
    )


def convert_to_hera_invocator_template(
    template: Template,
    hera_template_class: Type[BaseModel],
    template_type: Optional[BaseModel] = None,
) -> Tuple[str, List[str], List[str]]:
    hera_imports = [hera_template_class.__name__]
    model_imports = []

    template_keys = set(hera_template_class.__fields__.keys()).intersection(template.__fields__.keys())

    hera_template_str = [f"with {hera_template_class.__name__}("]
    for field in template.__fields__:
        if field in template_keys and getattr(template, field) is not None:
            val, sub_hera_imports, sub_model_imports = python_obj_to_repr(getattr(template, field))
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_model_imports)
            hera_template_str.append(f"{field}={val},")

    if template_type:
        template_field_keys = set(hera_template_class.__fields__.keys()).intersection(template_type.__fields__.keys())

        for field in template_type.__fields__:
            if hera_template_class == DAG and field == "tasks":
                # We create Task objects within the context
                continue
            elif hera_template_class == ContainerSet and field == "containers":
                continue

            if field in template_field_keys and getattr(template_type, field) is not None:
                val, sub_hera_imports, sub_model_imports = python_obj_to_repr(getattr(template_type, field))
                hera_imports.extend(sub_hera_imports)
                model_imports.extend(sub_model_imports)
                hera_template_str.append(f"{field}={val},")

    hera_template_str.append(") as invocator:")

    indent = " " * 8

    if hera_template_class == Steps and template.steps:
        for parallel_steps in template.steps:
            parallel_steps_list = parallel_steps.__root__
            if len(parallel_steps_list) > 1:
                hera_template_str.append(f"{indent}with invocator.parallel():")
                indent = " " * 12
            for step in parallel_steps.__root__:
                val, sub_hera_imports, sub_model_imports = convert_to_hera_equivalent(step, Step)
                hera_imports.extend(sub_hera_imports)
                model_imports.extend(sub_model_imports)
                hera_template_str.append(f"{indent}{val}")
            indent = " " * 8
    elif hera_template_class == DAG and template.dag:
        for task in template.dag.tasks:
            val, sub_hera_imports, sub_model_imports = convert_to_hera_equivalent(task, Task)
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_model_imports)
            hera_template_str.append(f"{indent}{val}")
    elif hera_template_class == ContainerSet and template.container_set:
        for container in template.container_set.containers:
            val, sub_hera_imports, sub_model_imports = convert_to_hera_equivalent(container, ContainerNode)
            hera_imports.extend(sub_hera_imports)
            model_imports.extend(sub_model_imports)
            hera_template_str.append(f"{indent}{val}")

    return (
        "\n".join(hera_template_str),
        hera_imports,
        model_imports,
    )


def template_to_python(template: Template) -> Tuple[str, List[str], List[str]]:
    if template.container is not None:
        return convert_to_hera_template(template, template.container, Container)
    elif template.script is not None:
        return convert_to_hera_template(template, template.script, Script)
    elif template.http is not None:
        return convert_to_hera_template(template, template.http, HTTP)
    elif template.data is not None:
        return convert_to_hera_template(template, template.data, Data)
    elif template.resource is not None:
        return convert_to_hera_template(template, template.resource, Resource)
    elif template.suspend is not None:
        return convert_to_hera_template(template, template.suspend, Suspend)
    elif template.dag is not None:
        return convert_to_hera_invocator_template(template, DAG, template.dag)
    elif template.steps is not None:
        return convert_to_hera_invocator_template(template, Steps)
    elif template.container_set is not None:
        return convert_to_hera_invocator_template(template, ContainerSet, template.container_set)
    else:
        # No-op (convert Template to itself) and rearrange imports
        val, hera_imports, model_imports = convert_to_hera_equivalent(template, Template)
        hera_imports.remove("Template")
        model_imports.append("Template")
        return val, hera_imports, model_imports


def model_to_python(model: BaseModel) -> Tuple[str, List[str], List[str]]:
    model_name = model.__class__.__name__
    if isinstance(model, Template):
        return template_to_python(model)

    hera_imports = []
    model_imports = [model_name]
    class_def = [f"{model_name}("]
    for attr in ChainMap(*(get_annotations(c) for c in model.__class__.__mro__)):
        if attr == "__slots__" or getattr(model, attr) is None:
            continue
        value = getattr(model, attr)
        assign_value, sub_hera_imports, sub_model_imports = python_obj_to_repr(value, type(value))
        hera_imports.extend(sub_hera_imports)
        model_imports.extend(sub_model_imports)

        class_def.append(f"{attr}={assign_value},")
    class_def.append(")")
    return "".join(class_def), hera_imports, model_imports


def build_file(
    file_builder: FileBuilder,
    hera_workflow_class: Type[Workflow],
    model_workflow: ModelWorkflow,
) -> FileBuilder:
    for attr, annotation in hera_workflow_class._get_all_annotations().items():
        if mappers := get_annotated_metadata(annotation, ModelMapperMixin.ModelMapper):
            if len(mappers) != 1:
                raise ValueError("Expected only one model mapper")
            if model_path := mappers[0].model_path:
                try:
                    if hera_workflow_class == CronWorkflow and attr == "suspend":
                        # Special case for CronWorkflow which has `cron_suspend` and `suspend`,
                        # which should go to the workflow_spec (but is also a valid attribute of
                        # CronWorkflow and exists in the model at the same model_path)
                        raise AttributeError()

                    value = _get_model_attr(model_workflow, model_path)
                except AttributeError:
                    if hera_workflow_class == CronWorkflow:
                        model_path = [model_path[0], "workflow_spec"] + model_path[1:]
                        try:
                            value = _get_model_attr(model_workflow, model_path)
                        except AttributeError:
                            continue
                    else:
                        continue

                if value is None:
                    continue

                if attr == "templates":
                    for template in value:
                        t_repr, sub_hera_imports, sub_model_imports = python_obj_to_repr(
                            template, get_args(unwrap_annotation(annotation))[0]
                        )
                        file_builder.hera_imports.extend(sub_hera_imports)
                        file_builder.model_imports.extend(sub_model_imports)
                        file_builder.context_def.append("    " + t_repr)
                else:
                    val_repr, sub_hera_imports, sub_model_imports = python_obj_to_repr(
                        value, unwrap_annotation(annotation)
                    )
                    file_builder.hera_imports.extend(sub_hera_imports)
                    file_builder.model_imports.extend(sub_model_imports)
                    file_builder.class_def.append(f"{attr}={val_repr},")

                    if attr == "workflow_template_ref":
                        file_builder.context_def.append("    pass")
    return file_builder


def workflow_to_python(model: ModelWorkflow) -> str:
    model_workflow_class = model.__class__.__name__
    if model_workflow_class == "Workflow":
        hera_workflow_class = Workflow
    elif model_workflow_class == "WorkflowTemplate":
        hera_workflow_class = WorkflowTemplate
    elif model_workflow_class == "ClusterWorkflowTemplate":
        hera_workflow_class = ClusterWorkflowTemplate
    elif model_workflow_class == "CronWorkflow":
        hera_workflow_class = CronWorkflow
    else:
        raise ValueError("Unrecognised model workflow class")

    file_builder = FileBuilder(
        hera_imports=[hera_workflow_class.__name__],
        class_def=[f"with {hera_workflow_class.__name__}("],
    )
    file_builder = build_file(file_builder, hera_workflow_class, model)

    imports = list(map(lambda x: f"from hera.workflows import {x}", set(file_builder.hera_imports)))
    imports.extend(map(lambda x: f"from hera.workflows.models import {x}", set(file_builder.model_imports)))

    return "\n".join(imports + file_builder.class_def + [") as w:"] + file_builder.context_def)


def join_workflows(workflows: Iterable[str]) -> str:
    """Join a collection of workflows into a single string."""
    return "\n".join(workflows)
