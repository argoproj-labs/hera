"""The `hera.workflows.task` module provides the Task and TaskResult classes.

See <https://argoproj.github.io/argo-workflows/walk-through/dag>
for more on using Tasks within a DAG.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum
from typing import Iterable, Iterator, List, Optional, Union

from hera.workflows._mixins import (
    ArgumentsMixin,
    ItemMixin,
    ParameterMixin,
    TemplateInvocatorSubNodeMixin,
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
    """The enumeration of Task Results.

    See Also:
        [Argo Depends Docs](https://argoproj.github.io/argo-workflows/enhanced-depends-logic/#depends)
    """

    failed = "Failed"
    succeeded = "Succeeded"
    errored = "Errored"
    skipped = "Skipped"
    omitted = "Omitted"
    daemoned = "Daemoned"
    any_succeeded = "AnySucceeded"
    all_failed = "AllFailed"

    def __or__(self, other: TaskResult) -> _TaskResultGroup:
        """Create an "or" condition over multiple TaskResults."""
        return _TaskResultGroup([self, other])


class _TaskResultGroup(Iterable[TaskResult]):
    """Private, implementation detail: an iterable of TaskResult with | support that maintains order and deduplicates."""

    __slots__ = ("_results",)

    def __init__(self, results: Iterable[TaskResult]):
        self._results: List[TaskResult] = []
        for r in results:
            if r not in self._results:
                self._results.append(r)

    def __or__(self, other: Union[Iterable[TaskResult], TaskResult]) -> _TaskResultGroup:
        if isinstance(other, TaskResult):
            return _TaskResultGroup(self._results + [other])
        return _TaskResultGroup(self._results + list(other))

    def __iter__(self) -> Iterator[TaskResult]:
        return iter(self._results)


OnType = Optional[Union[TaskResult, Iterable[TaskResult]]]


def _normalise_on(
    on: OnType,
    default: Optional[List[TaskResult]] = None,
) -> Optional[List[TaskResult]]:
    """Turn `on` into a list[TaskResult] or None.

    Accepts:
      - None -> return default (which may also be None)
      - TaskResult -> [TaskResult]
      - Iterable[TaskResult] -> list(...)
    """
    if on is None:
        return default
    if isinstance(on, TaskResult):
        return [on]
    return list(_TaskResultGroup(on))


_default_next_operator: ContextVar[Operator] = ContextVar("_default_next_operator", default=Operator.and_)
_default_next_on: ContextVar[Optional[List[TaskResult]]] = ContextVar("_default_on_operator", default=None)


class Task(
    TemplateInvocatorSubNodeMixin,
    ArgumentsMixin,
    ParameterMixin,
    ItemMixin,
):
    """Task is used to run a given template within a DAG. Must be instantiated under a DAG context."""

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
    def _subtype(self) -> str:
        return "tasks"

    def next(
        self,
        other: Task,
        operator: Optional[Operator] = None,
        on: OnType = None,
    ) -> Task:
        """Set self as a dependency of `other`."""
        operator = operator or _default_next_operator.get()
        on_list = _normalise_on(on, _default_next_on.get())

        # Build condition string:
        # - If multiple on-conditions: OR them and wrap in parens
        # - If single on-condition: A.succeeded
        # - If none: just "A"
        if on_list and len(on_list) > 1:
            condition_str = " || ".join(f"{self.name}.{c.value}" for c in on_list)
            condition_str = f"({condition_str})"
        elif on_list and len(on_list) == 1:
            condition_str = f"{self.name}.{on_list[0].value}"
        else:
            condition_str = self.name

        if other.depends is None:
            # First dependency
            other.depends = condition_str
        elif self.name in other._get_dependency_tasks():
            raise ValueError(f"{self.name} already in {other.name}'s depends: {other.depends}")
        else:
            # Add follow-up dependency
            other.depends += f" {operator} {condition_str}"

        return other

    @classmethod
    @contextmanager
    def set_next_defaults(
        cls,
        operator: Optional[Operator] = None,
        on: Union[TaskResult, Iterable[TaskResult], None] = None,
    ):
        """Temporarily modify the default behaviour of `next` and `>>`."""
        on_list = _normalise_on(on)

        operator_token = _default_next_operator.set(operator or _default_next_operator.get())
        on_token = _default_next_on.set(on_list)
        try:
            yield
        finally:
            _default_next_operator.reset(operator_token)
            _default_next_on.reset(on_token)

    def __rrshift__(self, other: List[Union[Task, str]]) -> Task:
        """Set `other` as a dependency self."""
        assert isinstance(other, list), f"Unknown type {type(other)} specified using reverse right bitshift operator"
        for o in other:
            if isinstance(o, Task):
                o.next(self)
            else:
                assert isinstance(o, str), (
                    f"Unknown list item type {type(o)} specified using reverse right bitshift operator"
                )
                if self.depends is None:
                    self.depends = o
                else:
                    self.depends += f" && {o}"
        return self

    def __rshift__(self, other: Union[Task, List[Task]]) -> Union[Task, List[Task]]:
        """Set self as a dependency of `other` which can be a single Task or list of Tasks."""
        if isinstance(other, Task):
            return self.next(other)
        elif isinstance(other, list):
            for o in other:
                assert isinstance(o, Task), (
                    f"Unknown list item type {type(o)} specified using right bitshift operator `>>`"
                )
                self.next(o)
            return other
        raise ValueError(f"Unknown type {type(other)} provided to `__rshift__`")

    def __or__(self, other: Union[Task, str]) -> str:
        """Return a condition of `self || other`."""
        if isinstance(other, Task):
            return f"({self.name} || {other.name})"
        assert isinstance(other, str), f"Unknown type {type(other)} specified using `|` operator"
        return f"{self.name} || {other}"

    def on_workflow_status(self, status: WorkflowStatus, op: Operator = Operator.equals) -> Task:
        """Sets the current task to run when the workflow finishes with the specified status."""
        expression = f"{{{{workflow.status}}}} {op} {status}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        return self

    def on_success(self, other: Task) -> Task:
        """Sets the current task to run when the given `other` task succeeds."""
        return self.next(other, on=TaskResult.succeeded)

    def on_failure(self, other: Task) -> Task:
        """Sets the current task to run when the given `other` task fails."""
        return self.next(other, on=TaskResult.failed)

    def on_error(self, other: Task) -> Task:
        """Sets the current task to run when the given `other` task errors."""
        return self.next(other, on=TaskResult.errored)

    def on_other_result(self, other: Task, value: str, operator: Operator = Operator.equals) -> Task:
        """Sets the current task to run when the given `other` task results in the specified `value` result."""
        expression = f"{other.result} {operator} {value}"
        if self.when:
            self.when += f" {Operator.and_} {expression}"
        else:
            self.when = expression
        other.next(self)
        return self

    def when_any_succeeded(self, other: Task) -> Task:
        """Sets the current task to run when the given `other` task succeedds."""
        assert (self.with_param is not None) or (self.with_sequence is not None), (
            "Can only use `when_all_failed` when using `with_param` or `with_sequence`"
        )

        return self.next(other, on=TaskResult.any_succeeded)

    def when_all_failed(self, other: Task) -> Task:
        """Sets the current task to run when the given `other` task has failed."""
        assert (self.with_param is not None) or (self.with_sequence is not None), (
            "Can only use `when_all_failed` when using `with_param` or `with_sequence`"
        )

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
            on_exit=self._build_on_exit(),
            template=_template,
            template_ref=self.template_ref,
            when=self.when,
            with_items=self._build_with_items(),
            with_param=self._build_with_param(),
            with_sequence=self.with_sequence,
        )


__all__ = ["Task", "TaskResult"]
