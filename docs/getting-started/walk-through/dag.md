# DAG

DAGs (Directed Acyclic Graphs) are similar to `Steps`, and in Hera, the syntax using context managers is exactly the same as `Steps`.
DAGs are formed of `Tasks`, and offer more flexibility in Workflow construction, with the key difference being that you
specify the dependencies of each `Task`, i.e. what other `Tasks` must run to completion before running this one.

## Specifying Dependencies

The classic example for the `DAG` is the "diamond":

```py
from hera.workflows import DAG, Workflow, script


@script()
def echo(message):
    print(message)


with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = echo(name="A", message="A")
        B = echo(name="B", message="B")
        C = echo(name="C", message="C")
        D = echo(name="D", message="D")

        A >> [B, C] >> D
```

Notice the `>>` (rshift) syntax used with the returned objects from the `echo` calls. The `echo` calls are returning
`Task` objects as the function is being called under a `DAG` context. Then, we can specify dependencies between `Tasks`
and lists of `Tasks` using the `>>` syntax. A list acts as a boolean `and` of the elements, and it is important to note
that a list cannot appear first in the chain or on both sides of a `>>`.

```py
        A >> [B, C] >> D
```

Here, with `A` first in the chain, it has no dependencies, so will run first. Then, with `[B, C]` depending on `A`, `B`
and `C` will both run in parallel once `A` has completed. Finally, `D` depends on `B` *and* `C`, so will run once they
have *both* completed. We can use the rshift syntax anywhere with `Tasks`, but it makes sense to keep it as the last
line of the `DAG` context.

## Parallel Steps Example as a DAG

If we look at the parallel steps example from [the Steps walk through](steps.md#parallel-steps), we can write a Workflow
using a `DAG` that behaves in the same way.

Looking at the `with Steps` section:

```py
    with Steps(name="steps") as s:
        echo(name="pre-parallel", message="Hello world!")

        with s.parallel():
            echo(name="parallel-1", message="I'm parallel-1!")
            echo(name="parallel-2", message="I'm parallel-2!")
            echo(name="parallel-3", message="I'm parallel-3!")

        echo(name="post-parallel", message="Goodbye world!")
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
        pre = echo(name="pre-parallel", message="Hello world!")
```

Next, `DAG`s don't have a `parallel` function so we can remove that line and de-indent the parallel steps, and we can
leave `post-parallel` as is. Remember we still need to assign variables!

```py
    with DAG(name="dag") as d:
        pre = echo(name="pre-parallel", message="Hello world!")
        parallel_1 = echo(name="parallel-1", message="I'm parallel-1!")
        parallel_2 = echo(name="parallel-2", message="I'm parallel-2!")
        parallel_3 = echo(name="parallel-3", message="I'm parallel-3!")
        post = echo(name="post-parallel", message="Goodbye world!")
```

Finally, we need to specify the dependencies, which will look very similar to the DAG diamond example.

```py
    with DAG(name="dag") as d:
        pre = echo(name="pre-parallel", message="Hello world!")
        parallel_1 = echo(name="parallel-1", message="I'm parallel-1!")
        parallel_2 = echo(name="parallel-2", message="I'm parallel-2!")
        parallel_3 = echo(name="parallel-3", message="I'm parallel-3!")
        post = echo(name="post-parallel", message="Goodbye world!")

        pre >> [parallel_1, parallel_2, parallel_3] >> post
```
