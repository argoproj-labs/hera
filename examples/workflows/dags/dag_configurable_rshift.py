"""This example shows how to override the defaults for the "next" function to configure the rshift (`>>`) behaviour.

This is useful if you want `A >> B` to mean "run B _only if_ A succeeded", otherwise the
[default depends logic](https://argo-workflows.readthedocs.io/en/latest/enhanced-depends-logic/) means `A >> B` is
equivalent to "B depends on `A.Succeeded || A.Skipped || A.Daemoned`".

By setting the values in `Task.set_next_defaults`, we can configure the rshift behaviour to use a different operator
and TaskResult. Then, the following

```py
with Task.set_next_defaults(operator=Operator.or_, on=TaskResult.succeeded):
    A >> [B, C] >> D
```

is equivalent to

```py
A.next(B, on=TaskResult.succeeded)
A.next(C, on=TaskResult.succeeded)
B.next(D, on=TaskResult.succeeded)
C.next(D, operator=Operator.or_, on=TaskResult.succeeded)
```

> Note the `Operator.or_` for D's `depends` is set when calling `C.next` which can also be confusing! This is because we
> use `next` to describe the forward relationships, while the Argo field is `depends` which describes the backward
> relationships.

Or, described using the backward relationship of `depends` (which only accepts strings):
```py
B.depends = "A.Succeeded"
C.depends = "A.Succeeded"
D.depends = "B.Succeeded || C.Succeeded"
```

> `set_next_defaults` also accepts lists or multiple values using the `|` operator!
"""

from hera.workflows import DAG, Task, TaskResult, Workflow, script
from hera.workflows.operator import Operator


@script(image="python:3.12")
def echo(message):
    print(message)


with Workflow(generate_name="dag-configurable-rshift-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})

        with Task.set_next_defaults(operator=Operator.or_, on=TaskResult.succeeded):
            A >> [B, C] >> D
