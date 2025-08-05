import ast
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, Optional, Set, Type, Union, cast

import black
import yaml

from hera._cli.base import GeneratePython
from hera._cli.generate.util import YAML_EXTENSIONS, convert_code, expand_paths, write_output
from hera.shared._pydantic import BaseModel
from hera.shared._type_util import (
    get_annotated_metadata,
)
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

if sys.version_info >= (3, 10):
    from types import NoneType
else:
    NoneType = type(None)

ModelWorkflow = Union[
    _ModelWorkflow,
    _ModelWorkflowTemplate,
    _ModelClusterWorkflowTemplate,
    _ModelCronWorkflow,
]

DEFAULT_EXTENSION = ".py"


def generate_python(options: GeneratePython):
    """Generate Python (Hera) Workflow definitions from YAML definitions.

    If the provided path is a folder, generates Python for all YAML files containing Workflows
    in that folder.
    """
    paths = sorted(expand_paths(options.from_, YAML_EXTENSIONS, recursive=options.recursive))

    path_to_output = convert_code(
        paths,
        options,
        loader_func=load_yaml_workflows,
        dumper_func=workflow_to_python,
        join_delimiter="\n",
    )

    write_output(
        options.to,
        path_to_output,
        extensions={DEFAULT_EXTENSION},
        default_extension=DEFAULT_EXTENSION,
        join_delimiter="\n",
    )


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


def workflow_to_python(model: ModelWorkflow) -> str:
    visitor = WorkflowPythonBuilder(model)
    return visitor.build()


class WorkflowPythonBuilder:
    """This class traverses a given model workflow and generates corresponding Python code using the Hera SDK."""

    def __init__(self, model: ModelWorkflow):
        self.model = model
        self.import_map: Dict[str, Set[str]] = defaultdict(set)

    def build(self) -> str:
        # Build the AST for the workflow
        hera_workflow_class = self._get_workflow_class(self.model)

        workflow_def = self._build_workflow_ast(hera_workflow_class)
        self._add_import("hera.workflows", hera_workflow_class.__name__)

        body = list(self._get_import_lines())
        body.append(workflow_def)

        module = ast.Module(body=body, type_ignores=[])
        module = ast.fix_missing_locations(module)

        # validate the generated code
        try:
            compile(module, filename="<string>", mode="exec")
        except SyntaxError as e:
            raise SyntaxError("Generated Python code contains syntax errors") from e

        # Format the generated code using Black if available
        module_code = ast.unparse(module)
        module_code = black.format_str(
            module_code,
            mode=black.FileMode(line_length=88, is_pyi=False),
        )
        return module_code

    def _add_import(self, module: str, name: str):
        self.import_map[module].add(name)

    def _get_import_lines(self) -> Iterator[ast.stmt]:
        for module, names in self.import_map.items():
            if not names:
                continue

            yield ast.ImportFrom(module=module, names=[ast.alias(name=name) for name in sorted(names)], level=0)

    def _get_workflow_class(self, model: ModelWorkflow) -> Type[Workflow]:
        model_workflow_class = model.__class__.__name__
        if model_workflow_class == "Workflow":
            return Workflow
        if model_workflow_class == "WorkflowTemplate":
            return WorkflowTemplate
        if model_workflow_class == "ClusterWorkflowTemplate":
            return ClusterWorkflowTemplate
        if model_workflow_class == "CronWorkflow":
            return CronWorkflow

        raise ValueError("Unrecognised model workflow class")

    def _build_workflow_ast(
        self,
        hera_workflow_class: Type[Workflow],
    ) -> ast.stmt:
        keywords: List[ast.keyword] = []
        body = []

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

                        value = _get_model_attr(self.model, model_path)
                    except AttributeError:
                        if hera_workflow_class == CronWorkflow:
                            model_path = [model_path[0], "workflow_spec"] + model_path[1:]
                            try:
                                value = _get_model_attr(self.model, model_path)
                            except AttributeError:
                                continue
                        else:
                            continue

                    if value is None:
                        continue

                    if attr == "templates":
                        for template in value:
                            if not isinstance(template, Template):
                                raise ValueError(f"Expected template to be a Template, got {type(template)}")

                            body.append(self._build_statement(template))
                    else:
                        value = self._build_expression(value)
                        keywords.append(
                            ast.keyword(
                                arg=attr,
                                value=value,
                            )
                        )

                        if attr == "workflow_template_ref":
                            body.append(ast.Pass())
                            pass

        if len(body) == 0:
            body.append(ast.Pass())

        with_item = ast.withitem(
            context_expr=ast.Call(
                func=ast.Name(id=hera_workflow_class.__name__, ctx=ast.Load()),
                args=[],
                keywords=keywords,
            ),
            optional_vars=ast.Name(id="w", ctx=ast.Store()),
        )
        return ast.With(items=[with_item], body=body)

    def _build_expression(
        self,
        value: Any,
    ) -> ast.expr:
        # Primitive types
        if isinstance(value, (str, bool, int, float, NoneType)):
            return ast.Constant(value=value)

        # Collections
        if isinstance(value, list):
            return ast.List(
                elts=[self._build_expression(v) for v in value],
                ctx=ast.Load(),
            )
        if isinstance(value, dict):
            keys: List[Optional[ast.expr]] = []
            values = []
            for k, v in value.items():
                keys.append(self._build_expression(k))
                values.append(self._build_expression(v))
            return ast.Dict(
                keys=keys,
                values=values,
            )

        # Model instances
        if isinstance(value, BaseModel):
            model_name = value.__class__.__name__
            self._add_import("hera.workflows.models", model_name)
            keywords: List[ast.keyword] = []
            for attr in value.__fields__:
                if attr == "__slots__" or getattr(value, attr) is None:
                    continue
                attribute_value = getattr(value, attr)
                keywords.append(
                    ast.keyword(
                        arg=attr,
                        value=self._build_expression(attribute_value),
                    )
                )

            return ast.Call(
                func=ast.Name(id=model_name, ctx=ast.Load()),
                args=[],
                keywords=keywords,
            )

        raise ValueError(f"Unsupported type: {type(value)} for value {value}")

    def _build_statement(self, template: Template) -> ast.stmt:
        if template.container is not None:
            return self._build_hera_template_statement(template, template.container, Container)
        if template.script is not None:
            return self._build_hera_template_statement(template, template.script, Script)
        if template.http is not None:
            return self._build_hera_template_statement(template, template.http, HTTP)
        if template.data is not None:
            return self._build_hera_template_statement(template, template.data, Data)
        if template.resource is not None:
            return self._build_hera_template_statement(template, template.resource, Resource)
        if template.suspend is not None:
            return self._build_hera_template_statement(template, template.suspend, Suspend)
        if template.dag is not None:
            return self._build_hera_invocator_template_statement(template, DAG, template.dag)
        if template.steps is not None:
            return self._build_hera_invocator_template_statement(template, Steps)
        if template.container_set is not None:
            return self._build_hera_invocator_template_statement(template, ContainerSet, template.container_set)

        # No-op (convert Template to itself) and rearrange imports
        return self._build_template_call_expression(template, Template)

    def _build_hera_template_statement(
        self,
        template: Template,
        template_type_field: BaseModel,
        hera_template_class: Type[BaseModel],
    ) -> ast.stmt:
        self._add_import("hera.workflows", hera_template_class.__name__)

        template_keys = set(hera_template_class.__fields__.keys()).intersection(template.__fields__.keys())
        template_type_field_keys = set(hera_template_class.__fields__.keys()).intersection(
            template_type_field.__fields__.keys()
        )

        keywords: List[ast.keyword] = []
        for field in template.__fields__:
            # Special case for http which shouldn't be a field in template_keys (but is)
            if field in template_keys and getattr(template, field) is not None and field != "http":
                val = self._build_expression(getattr(template, field))
                keywords.append(
                    ast.keyword(
                        arg=field,
                        value=val,
                    )
                )

            if field == "metadata" and getattr(template, field) is not None:
                metadata = cast(Metadata, getattr(template, field))
                if metadata.labels:
                    labels = self._build_expression(metadata.labels)
                    keywords.append(
                        ast.keyword(
                            arg="labels",
                            value=labels,
                        )
                    )

                if metadata.annotations:
                    annotations = self._build_expression(metadata.annotations)
                    keywords.append(
                        ast.keyword(
                            arg="annotations",
                            value=annotations,
                        )
                    )

        for field in template_type_field.__fields__:
            if field in template_type_field_keys and getattr(template_type_field, field) is not None:
                val = self._build_expression(getattr(template_type_field, field))
                keywords.append(
                    ast.keyword(
                        arg=field,
                        value=val,
                    )
                )

        # Special case for Data template transformation
        if hera_template_class == Data and template.data and template.data.transformation:
            keywords.append(
                ast.keyword(
                    arg="transformations",
                    value=ast.List(
                        elts=[
                            ast.Constant(value=transformation.expression)
                            for transformation in template.data.transformation
                        ],
                        ctx=ast.Load(),
                    ),
                )
            )

        return ast.Expr(
            value=ast.Call(
                func=ast.Name(id=hera_template_class.__name__, ctx=ast.Load()),
                args=[],
                keywords=keywords,
            )
        )

    def _build_hera_invocator_template_statement(
        self,
        template: Template,
        hera_template_class: Type[BaseModel],
        template_type: Optional[BaseModel] = None,
    ) -> ast.stmt:
        self._add_import("hera.workflows", hera_template_class.__name__)
        template_keys = set(hera_template_class.__fields__.keys()).intersection(template.__fields__.keys())

        body: List[ast.stmt] = []
        keywords: List[ast.keyword] = []

        for field in template.__fields__:
            if field in template_keys and getattr(template, field) is not None:
                val = self._build_expression(getattr(template, field))
                keywords.append(ast.keyword(arg=field, value=val))

        if template_type:
            template_field_keys = set(hera_template_class.__fields__.keys()).intersection(
                template_type.__fields__.keys()
            )

            for field in template_type.__fields__:
                if hera_template_class == DAG and field == "tasks":
                    # We create Task objects within the context
                    continue
                elif hera_template_class == ContainerSet and field == "containers":
                    continue

                if field in template_field_keys and getattr(template_type, field) is not None:
                    val = self._build_expression(getattr(template_type, field))
                    keywords.append(ast.keyword(arg=field, value=val))

        if hera_template_class == Steps and template.steps:
            invocator_type = "steps"
            for parallel_steps in template.steps:
                parallel_steps_list = parallel_steps.__root__

                if len(parallel_steps_list) > 1:
                    body.append(
                        ast.With(
                            items=[
                                ast.withitem(
                                    context_expr=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(id=invocator_type, ctx=ast.Load()),
                                            attr="parallel",
                                            ctx=ast.Load(),
                                        ),
                                        args=[],
                                        keywords=[],
                                    ),
                                )
                            ],
                            body=[
                                self._build_template_call_expression(step, Step) for step in parallel_steps.__root__
                            ],
                        )
                    )
                else:
                    step = parallel_steps_list[0]
                    body.append(self._build_template_call_expression(step, Step))
        elif hera_template_class == DAG and template.dag:
            invocator_type = "dag"
            for task in template.dag.tasks:
                body.append(self._build_template_call_expression(task, Task))
        elif hera_template_class == ContainerSet and template.container_set:
            invocator_type = "container_set"
            for container in template.container_set.containers:
                body.append(self._build_template_call_expression(container, ContainerNode))
        else:
            raise ValueError(
                f"Unsupported hera_template_class: {hera_template_class.__name__} for template: {template}"
            )

        return ast.With(
            items=[
                ast.withitem(
                    context_expr=ast.Call(
                        func=ast.Name(id=hera_template_class.__name__, ctx=ast.Load()),
                        args=[],
                        keywords=keywords,
                    ),
                    optional_vars=ast.Name(id=invocator_type, ctx=ast.Store()),
                )
            ],
            body=body,
        )

    def _build_template_call_expression(
        self,
        model_class_obj: BaseModel,
        hera_class: Type[BaseModel],
    ) -> ast.stmt:
        self._add_import("hera.workflows", hera_class.__name__)

        template_keys = set(model_class_obj.__fields__.keys()).intersection(hera_class.__fields__.keys())

        keywords: List[ast.keyword] = []
        for field in hera_class.__fields__:
            if field in template_keys and getattr(model_class_obj, field) is not None:
                val = self._build_expression(getattr(model_class_obj, field))
                keywords.append(
                    ast.keyword(
                        arg=field,
                        value=val,
                    )
                )

        return ast.Expr(
            value=ast.Call(
                func=ast.Name(id=hera_class.__name__, ctx=ast.Load()),
                args=[],
                keywords=keywords,
            )
        )
