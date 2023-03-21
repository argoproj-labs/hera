from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from hera.workflows._mixins import (
    ArgumentsMixin,
    ItemMixin,
    ParameterMixin,
    SubNodeMixin,
    TemplateInvocatorMixin,
    TemplateMixin,
)
from hera.workflows.models import (
    DAGTask as _ModelDAGTask,
    Template,
)
from hera.workflows.operator import Operator
from hera.workflows.protocol import Templatable
from hera.workflows.workflow_status import WorkflowStatus


class TaskResult(Enum):
    failed = "Failed"
    succeeded = "Succeeded"
    errored = "Errored"
    skipped = "Skipped"
    omitted = "Omitted"
    daemoned = "Daemoned"
    any_succeeded = "AnySucceeded"
    all_failed = "AllFailed"


class Task(
    TemplateInvocatorMixin,
    ArgumentsMixin,
    SubNodeMixin,
    ParameterMixin,
    ItemMixin,
):
    dependencies: Optional[List[str]] = None
    depends: Optional[str] = None

    def _get_dependency_tasks(self) -> List[str]:
        if self.depends is None:
            return []

        # filter out operators
        all_operators = [o for o in Operator]
        tasks = [t for t in self.depends.split() if t not in all_operators]

        # remove dot suffixes
        task_names = [t.split(".")[0] for t in tasks]
        return task_names

    @property
    def id(self) -> str:
        return f"{{{{tasks.{self.name}.id}}}}"

    @property
    def ip(self) -> str:
        return f"{{{{tasks.{self.name}.ip}}}}"

    @property
    def status(self) -> str:
        return f"{{{{tasks.{self.name}.status}}}}"

    @property
    def exit_code(self) -> str:
        return f"{{{{tasks.{self.name}.exitCode}}}}"

    @property
    def started_at(self) -> str:
        return f"{{{{tasks.{self.name}.startedAt}}}}"

    @property
    def finished_at(self) -> str:
        return f"{{{{tasks.{self.name}.finishedAt}}}}"

    @property
    def result(self) -> str:
        return f"{{{{tasks.{self.name}.outputs.result}}}}"

    def next(self, other: Task, operator: Operator = Operator.and_, on: Optional[TaskResult] = None) -> Task:
        assert issubclass(other.__class__, Task)

        condition = f".{on}" if on else ""

        if other.depends is None:
            # First dependency
            other.depends = self.name + condition
        elif self.name in other._get_dependency_tasks():
            raise ValueError(f"{self.name} already in {other.name}'s depends: {other.depends}")
        else:
            # Add follow-up dependency
            other.depends += f" {operator} {self.name + condition}"
        return other

    def __rrshift__(self, other: List[Task]) -> Task:
        assert isinstance(other, list), f"Unknown type {type(other)} specified using reverse right bitshift operator"
        for o in other:
            o.next(self)
        return self

    def __rshift__(self, other: Union["Task", List["Task"]]) -> Union[Task, List[Task]]:
        if isinstance(other, Task):
            return self.next(other)
        elif isinstance(other, list):
            for o in other:
                assert isinstance(
                    o, Task
                ), f"Unknown list item type {type(o)} specified using right bitshift operator `>>`"
                self.next(o)
            return other
        raise ValueError(f"Unknown type {type(other)} provided to `__rshift__`")

    def on_workflow_status(self, status: WorkflowStatus, op: Operator = Operator.equals) -> Task:
        expression = f"{{{{workflow.status}}}} {op} {status}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        return self

    def on_success(self, other: Task) -> Task:
        return self.next(other, on=TaskResult.succeeded)

    def on_failure(self, other: Task) -> Task:
        return self.next(other, on=TaskResult.failed)

    def on_error(self, other: Task) -> Task:
        return self.next(other, on=TaskResult.errored)

    def on_other_result(self, other: Task, value: str, operator: Operator = Operator.equals) -> Task:
        expression = f"{other.result} {operator} {value}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        other.next(self)
        return self

    def when_any_succeeded(self, other: Task) -> Task:
        assert (self.with_param is not None) or (
            self.with_sequence is not None
        ), "Can only use `when_all_failed` when using `with_param` or `with_sequence`"

        return self.next(other, on=TaskResult.any_succeeded)

    def when_all_failed(self, other: Task) -> Task:
        assert (self.with_param is not None) or (
            self.with_sequence is not None
        ), "Can only use `when_all_failed` when using `with_param` or `with_sequence`"

        return self.next(other, on=TaskResult.all_failed)

    def _build_dag_task(self) -> _ModelDAGTask:
        _template = None
        if isinstance(self.template, str):
            _template = self.template
        elif isinstance(self.template, (Template, TemplateMixin)):
            _template = self.template.name

        _inline = None
        if isinstance(self.inline, Template):
            _inline = self.inline
        elif isinstance(self.inline, Templatable):
            _inline = self.inline._build_template()

        return _ModelDAGTask(
            arguments=self._build_arguments(),
            continue_on=self.continue_on,
            dependencies=self.dependencies,
            depends=self.depends,
            hooks=self.hooks,
            inline=_inline,
            name=self.name,
            on_exit=self.on_exit,
            template=_template,
            template_ref=self.template_ref,
            when=self.when,
            with_items=self._build_with_items(),
            with_param=self._build_with_param(),
            with_sequence=self.with_sequence,
        )


__all__ = ["Task", "TaskResult"]
