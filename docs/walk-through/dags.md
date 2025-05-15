# DAGs

DAGs (Directed Acyclic Graphs) are similar to `Steps`, and the syntax to use DAGs is exactly the same. DAGs are formed
of `Tasks`, and offer more flexibility in Workflow construction, with the key difference being that you can specify the
dependencies of each `Task`, i.e. which other `Tasks` must run to completion before running this one, and Argo will
construct the graph and run the Tasks in the desired order.

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
chain or on both sides of a `>>`.

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
