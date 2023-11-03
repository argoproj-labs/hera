# DAG

DAGs (Directed Acyclic Graphs) are similar to `Steps`, and in Hera, the syntax using context managers is exactly the same as `Steps`.
DAGs are formed of `Tasks`, and offer more flexibility in Workflow construction, with the key difference being that you
specify the dependencies of each `Task`, i.e. which other `Tasks` must run to completion before running this one.

## Specifying Dependencies

The classic example for the `DAG` is the "diamond":

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

Notice the `>>` (rshift) syntax used with the returned objects from the `echo` calls; it specifies the left-hand-side of
the operator is a dependency of the right-hand-side, i.e. `A >> B` means "B depends on A". This is syntactic sugar for
`A.next(B)`, see the [Task dependencies explained](#task-dependencies-explained) section for more examples.

The `echo` calls are returning `Task` objects as the function is being called under a `DAG` context. Then, we can
specify dependencies between `Tasks` and lists of `Tasks` using the `>>` syntax. A list acts as a boolean `and` of the
elements, and it is important to note that a list cannot appear first in the chain or on both sides of a `>>`.

```py
        A >> [B, C] >> D
```

Here, with `A` first in the chain, it has no dependencies, so will run first. Then, with `[B, C]` depending on `A`, `B`
and `C` will both run in parallel once `A` has completed. Finally, `D` depends on `B` *and* `C`, so will run once they
have *both* completed. We can use the rshift syntax anywhere with `Tasks`, but it makes sense to keep it as the last
line of the `DAG` context.

### Flexible depends syntax

It's not necessary to set all the dependencies on a single line! Writing 

```python
A >> [B, C] >> D
``` 

is equivalent to writing

```python
A >> B >> D
A >> C >> D
```

or

```python
A >> B
B >> D

A >> C
C >> D
```

This means that you can incrementally build up your DAG, add dependencies as you go, define tasks wherever, and even
import scripts from some place other than the file where the Workflow/DAG are used!

## Parallel Steps Example as a DAG

If we look at the parallel steps example from [the Steps walk through](steps.md#parallel-steps), we can write a Workflow
using a `DAG` that behaves in the same way.

Looking at the `with Steps` section:

```py
    with Steps(name="steps") as s:
        echo(name="pre-parallel", arguments={"message": "Hello world!"})

        with s.parallel():
            echo(name="parallel-1", arguments={"message": "I'm parallel-1!"})
            echo(name="parallel-2", arguments={"message": "I'm parallel-2!"})
            echo(name="parallel-3", arguments={"message": "I'm parallel-3!"})

        echo(name="post-parallel", arguments={"message": "Goodbye world!"})
```

First, remember to change your imports to get the `DAG` class:

```py
from hera.workflows import DAG, Workflow, script
```

Then, going line-by-line, we can build a DAG starting by changing the context manager to a `DAG`, and we can keep the
`pre-parallel` call the same, as it will now create a `Task`. However, we need to keep track of the created `Task`, so
let's assign it to a variable:

```py
    with DAG(name="dag") as d:
        pre = echo(name="pre-parallel", arguments={"message": "Hello world!"})
```

Next, `DAG`s don't have a `parallel` function so we can remove that line and de-indent the parallel steps, and we can
leave `post-parallel` as is. Remember we still need to assign variables!

```py
    with DAG(name="dag") as d:
        pre = echo(name="pre-parallel", arguments={"message": "Hello world!"})
        parallel_1 = echo(name="parallel-1", arguments={"message": "I'm parallel-1!"})
        parallel_2 = echo(name="parallel-2", arguments={"message": "I'm parallel-2!"})
        parallel_3 = echo(name="parallel-3", arguments={"message": "I'm parallel-3!"})
        post = echo(name="post-parallel", arguments={"message": "Goodbye world!"})
```

Finally, we need to specify the dependencies, which will look very similar to the DAG diamond example.

```py
    with DAG(name="dag") as d:
        pre = echo(name="pre-parallel", arguments={"message": "Hello world!"})
        parallel_1 = echo(name="parallel-1", arguments={"message": "I'm parallel-1!"})
        parallel_2 = echo(name="parallel-2", arguments={"message": "I'm parallel-2!"})
        parallel_3 = echo(name="parallel-3", arguments={"message": "I'm parallel-3!"})
        post = echo(name="post-parallel", arguments={"message": "Goodbye world!"})

        pre >> [parallel_1, parallel_2, parallel_3] >> post
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

As a diagram:

```
A
|
B
```

`A >> B` is equivalent to `A.next(B)`.

## Lists of Tasks

A list of Tasks used with the rshift syntax helps to describe multiple dependencies at once.

* A single Task on the left side of `>>` and a list Tasks on the right side is shorthand for specifying that each Task
  in the list independently depends on the single left-side Task and will all start once that Task has a task result of
  `Succeeded || Skipped || Daemoned`
* A list of Tasks on the left of `>>` and a single Task on the right describes that the single Task will only run once
  _all_ the Tasks in the list have the task result of `Succeeded || Skipped || Daemoned`
* A list of Tasks on both sides of `>>` is not supported, and multiple dependency statements should be used


### Example 1

To create a DAG diamond, we have the option to use the list syntax in the middle of the dependency syntax:

```py
A = Task(...)
B = Task(...)
C = Task(...)
D = Task(...)
A >> [B, C] >> D
```

describes the relationships:

* "A has no dependencies
* "B depends on A; C depends on A"
* "D depends on B AND C"

As a diagram:

```
  A
 / \
B   C
 \ /
  D
```

### Example 2

In this DAG, we **have to** describe the dependencies over multiple statements, as `[A, B] >> [C, D]` is not valid syntax:

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