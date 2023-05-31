"""The task module provides the Task and TaskResult classes.

See https://argoproj.github.io/argo-workflows/walk-through/dag/
for more on using Tasks within a DAG.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from hera.workflows._mixins import (
    ArgumentsMixin,
    ItemMixin,
    ParameterMixin,
    SubNodeMixin,
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
    """The enumeration of Task Results specified at
    https://argoproj.github.io/argo-workflows/enhanced-depends-logic/#depends
    """

    failed = "Failed"
    succeeded = "Succeeded"
    errored = "Errored"
    skipped = "Skipped"
    omitted = "Omitted"
    daemoned = "Daemoned"
    any_succeeded = "AnySucceeded"
    all_failed = "AllFailed"


class Task(
    TemplateInvocatorSubNodeMixin,
    ArgumentsMixin,
    SubNodeMixin,
    ParameterMixin,
    ItemMixin,
):
    """Task is used to run a given template within a DAG. Must be instantiated under a DAG context.

## Dependencies

Any `Tasks` without a dependency defined will start immediately.

Dependencies between Tasks can be described using the convenience syntax `>>`, for example:

```py
    A = Task(...)
    B = Task(...)
    A >> B
```

describes the relationships:

* "A has no dependencies (so starts immediately)
* "B depends on A".

As a diagram:

```
A
|
B
```

`A >> B` is equivalent to `A.next(B)`.

## Lists of Tasks

A list of Tasks used with the rshift syntax describes an "AND" dependency between the single Task on the left of
`>>` and the list Tasks to the right of `>>` (or vice versa). A list of Tasks on both sides of `>>` is not supported.

For example:

```
    A = Task(...)
    B = Task(...)
    C = Task(...)
    D = Task(...)
    A >> [B, C] >> D
```

describes the relationships:

* "A has no dependencies
* "B AND C depend on A"
* "D depends on B AND C"

As a diagram:

```
  A
 / \\
B   C
 \ /
  D
```

Dependencies can be described over multiple statements:

```
    A = Task(...)
    B = Task(...)
    C = Task(...)
    D = Task(...)
    A >> [C, D]
    B >> [C, D]
```

describes the relationships:

* "A and B have no dependencies
* "C depends on A AND B"
* "D depends on A AND B"

As a diagram:

```
A   B
| X |
C   D
```
    """

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

    def next(self, other: Task, operator: Operator = Operator.and_, on: Optional[TaskResult] = None) -> Task:
        """Set self as a dependency of `other`."""
        assert issubclass(other.__class__, Task)

        condition = f".{on.value}" if on else ""

        if other.depends is None:
            # First dependency
            other.depends = self.name + condition
        elif self.name in other._get_dependency_tasks():
            raise ValueError(f"{self.name} already in {other.name}'s depends: {other.depends}")
        else:
            # Add follow-up dependency
            other.depends += f" {operator} {self.name + condition}"
        return other

    def __rrshift__(self, other: List[Union[Task, str]]) -> Task:
        """Set `other` as a dependency self."""
        assert isinstance(other, list), f"Unknown type {type(other)} specified using reverse right bitshift operator"
        for o in other:
            if isinstance(o, Task):
                o.next(self)
            else:
                assert isinstance(
                    o, str
                ), f"Unknown list item type {type(o)} specified using reverse right bitshift operator"
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
                assert isinstance(
                    o, Task
                ), f"Unknown list item type {type(o)} specified using right bitshift operator `>>`"
                self.next(o)
            return other
        raise ValueError(f"Unknown type {type(other)} provided to `__rshift__`")

    def __or__(self, other: Union[Task, str]) -> str:
        """Adds a condition of"""
        if isinstance(other, Task):
            return f"({self.name} || {other.name})"
        assert isinstance(other, str), f"Unknown type {type(other)} specified using `|` operator"
        return f"{self.name} || {other}"

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
            on_exit=self._build_on_exit(),
            template=_template,
            template_ref=self.template_ref,
            when=self.when,
            with_items=self._build_with_items(),
            with_param=self._build_with_param(),
            with_sequence=self.with_sequence,
        )


__all__ = ["Task", "TaskResult"]
