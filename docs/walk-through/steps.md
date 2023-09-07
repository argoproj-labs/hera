# Steps

Steps are a relatively simple feature to run through a series of executable steps on Argo. They can be more flexible and
powerful with parallel steps and `when` clauses.

Basic `Steps` usage involves creating a `Steps` object as a context manager, and referencing templates or initializing
multiple `Step` objects within the context, which are automatically added to the `Steps` context manager. In Hera, when
referencing a single function decorated with `@script` multiple times under a single `Steps` context, you must pass in a
unique `name` (the *step*'s name) for each call.

```py
from hera.workflows import Steps, Workflow, WorkflowsService, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        echo(name="hello", arguments={"message": "Hello world!"})
        echo(name="goodbye", arguments={"message": "Goodbye world!"})

w.create()
```

## Parallel Steps

As the name suggests, Parallel Steps are a way to run multiple steps concurrently. In Hera, this is done by creating a
sub-context under a `Steps` context manager by using the context manager object's `parallel()` function. We can still
use sequential steps before and after the parallel context!

```py
from hera.workflows import Steps, Workflow, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
) as w:
    with Steps(name="steps") as s:
        echo(name="pre-parallel", arguments={"message": "Hello world!"})

        with s.parallel():
            echo(name="parallel-1", arguments={"message": "I'm parallel-1!"})
            echo(name="parallel-2", arguments={"message": "I'm parallel-2!"})
            echo(name="parallel-3", arguments={"message": "I'm parallel-3!"})

        echo(name="post-parallel", arguments={"message": "Goodbye world!"})

w.create()
```

Remember any parallel steps will run indeterminately within the context, so `parallel-1`, `parallel-2` and `parallel-3`
could run in any order, but `pre-parallel` will always run before the parallel steps and `post-parallel` will run after
*all* the parallel steps have completed.

## `when` Clauses

A `when` clause specifies the conditions under which the step or task will run. Examples of `when` clauses can be found
throughout the examples, such as [the Argo coinflip example](../examples/workflows/upstream/coinflip.md).

If we consider features offered by Hera along with what we've learned about parameters and parallel steps, we
can form a Workflow with identical behaviour to the upstream coinflip, but using only Python scripts and syntactic sugar
functions, which makes for more readable and maintainable code!


```py
from hera.workflows import Steps, Workflow, script


@script()
def flip():
    import random

    result = "heads" if random.randint(0, 1) == 0 else "tails"
    print(result)


@script()
def it_was(coin_result):
    print(f"it was {coin_result}")


with Workflow(generate_name="coinflip-", entrypoint="steps") as w:
    with Steps(name="steps") as s:
        f = flip()
        with s.parallel():
            it_was(name="heads", arguments={"coin_result": "heads"}, when=f'{f.result} == "heads"')
            it_was(name="tails", arguments={"coin_result": "tails"}, when=f'{f.result} == "tails"')
```

<details><summary>Click to see an example Workflow log</summary>

```console
coinflip-gfrws-flip-1899249874: heads
coinflip-gfrws-it-was-2809981541: it was heads
```

</details>

For more about `when` clauses, see the [Conditionals](conditionals.md) page!
