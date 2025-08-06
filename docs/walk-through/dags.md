# DAGs

DAGs (Directed Acyclic Graphs) are formed of `Tasks`. They are similar to `Steps`, using a context manager in the same
way, but offer more flexibility in Workflow construction, with the key difference being that you must specify any
dependencies of each `Task` using the right-shift (`>>`) syntax. This tells Argo which other `Tasks` must run to
completion before running this one. When the Workflow is submitted, Argo will construct the graph and run the Tasks in
the desired order.

## Specifying Dependencies

The classic example for the `DAG` is the "diamond":


=== "Hera"

    ```py
    from hera.workflows import DAG, Workflow, script


    @script()
    def echo(message):
        print(message)


    with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
        with DAG(name="diamond"):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "B"})
            C = echo(name="C", arguments={"message": "C"})
            D = echo(name="D", arguments={"message": "D"})

            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python

    ```

The rshift syntax (`>>`) is used with the returned objects from the `echo` calls; it specifies the left-hand-side of the
operator is a dependency of the right-hand-side, i.e. `A >> B` means "B depends on A". This is syntactic sugar for
`A.next(B)`, see the [Task dependencies explained](#task-dependencies-explained) section for more examples. A list acts
as a boolean `and` of all the elements of the list, and it is important to note that a list cannot appear first in the
chain or on both sides of a `>>` (due to Python language limitations).

```py
        A >> [B, C] >> D
```

Here, with `A` first in the chain, it has no dependencies, so will run first. Then, with `[B, C]` depending on `A`, `B`
and `C` will both run in parallel once `A` has completed. Finally, `D` depends on `B` *and* `C`, so will run once they
have *both* completed.

It's not necessary to set all the dependencies on a single line. The examples below are all equivalent:

=== "Single line"

    ```python
    A >> [B, C] >> D
    ``` 

=== "Alternative 1"

    ```python
    A >> B >> D
    A >> C >> D
    ```

=== "Alternative 2"

    ```python
    A >> B
    B >> D

    A >> C
    C >> D
    ```

This means that you can incrementally build up your DAG, add dependencies as you go, define tasks wherever, and even
import scripts from some place other than the file where the Workflow/DAG are used.

## Parallel Steps Example as a DAG

We can convert the Parallel Steps example from [the Steps walkthrough](steps.md#parallel-steps) into a DAG, by removing the `parallel()` context, and specifying the dependencies:

=== "Parallel Steps"

    ```py
    with Steps(name="steps") as s:
        echo(name="pre-parallel", arguments={"message": "Hello world!"})

        with s.parallel():
            echo(name="parallel-1", arguments={"message": "I'm parallel-1!"})
            echo(name="parallel-2", arguments={"message": "I'm parallel-2!"})
            echo(name="parallel-3", arguments={"message": "I'm parallel-3!"})

        echo(name="post-parallel", arguments={"message": "Goodbye world!"})
    ```

=== "DAG Equivalent"

    ```py
    with DAG(name="dag") as d:
        pre = echo(name="pre-parallel", arguments={"message": "Hello world!"})
        p1 = echo(name="parallel-1", arguments={"message": "I'm parallel-1!"})
        p2 = echo(name="parallel-2", arguments={"message": "I'm parallel-2!"})
        p3 = echo(name="parallel-3", arguments={"message": "I'm parallel-3!"})
        post = echo(name="post-parallel", arguments={"message": "Goodbye world!"})

        pre >> [p1, p2, p3] >> post
    ```

## Task dependencies explained

Any `Tasks` without a dependency defined will start immediately.

Dependencies between Tasks can be described using the convenience syntax `>>`, which follows the default
[depends logic](https://argoproj.github.io/argo-workflows/enhanced-depends-logic/#depends) of Argo, for example:

```py
A = Task(...)
B = Task(...)
A >> B
```

describes the relationships:

* "A has no dependencies (so starts immediately)
* "B depends on `A.Succeeded || A.Skipped || A.Daemoned`.

More complex dependencies can be described using `depends`, for example, to run B if A has failed or errored, and run C
only if A succeeded:

```py
from hera.workflows import Operator, Task, TaskResult

A = Task(...)
B = Task(...)
C = Task(...)

B.depends = "A.Failed || A.Errored"
C.depends = "A.Succeeded"
```

## Lists of Tasks

A list of Tasks used with the rshift syntax helps to describe multiple dependencies at once.

* A single Task on the left side of `>>` and a list Tasks on the right side is shorthand for specifying
  that each Task in the list independently depends on the single left-side Task.
* A list of Tasks on the left of `>>` and a single Task on the right describes that the single Task will only run once
  _all_ the Tasks finish. Note, a list of Tasks cannot be first in a chain of dependencies.
* A list of Tasks on both sides of `>>` is _not supported_, and multiple dependency statements should be used.

### Example

In this DAG, we must describe the dependencies over multiple statements, as `[A, B] >> [C, D]` is not valid syntax:

```py
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

## Configuring the Default "Next" Behaviour for `>>`

Hera v5.24 added the `Task.set_next_defaults` function, allowing you to set the default `operator` and `on` values
within a scoped context, which by extension allows you to configure the rshift (`>>`) behaviour.

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

The `set_next_defaults` function also accepts lists or values applying the `|` operator for the `on` value, meaning you can also specify conditions like `B.depends = "A.Succeeded || A.Daemoned"`, without affecting the `operator` used. E.g:

```py
with Task.set_next_defaults(operator=Operator.and_, on=TaskResult.succeeded | TaskResult.skipped):
    [task_a, task_b] >> task_c

assert task_c.depends == "(task-a.Skipped || task-a.Succeeded) && (task-b.Skipped || task-b.Succeeded)"
```

See the [DAG Configurable rshift example](../examples/workflows/dags/dag_configurable_rshift.md) for the full code!
