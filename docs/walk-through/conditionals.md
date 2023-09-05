# Conditionals

Conditional execution of steps and tasks is available through the [basic `when` clause](#basic-when-clauses), along with
more complex [expressions](#complex-when-clauses) and [`Task` functions](#improved-task-conditionals).

## Basic `when` Clauses

Argo uses [`govaluate`](https://github.com/Knetic/govaluate) in its `when` expressions - Hera is compatible with these
`when` expression if you write them in literal strings, however, without prior Argo knowledge, you may not know the
chain of keys to access steps and their parameters.

You can instead use `Parameters` and the special `result` parameter in an f-string to make your code more readable:

```py
run_script(
    ...,
    when=f'{previous_step.get_parameter("some-parameter")} == "some-value"'
)
```

is equivalent to

```py
run_script(
    ...,
    when='{{steps.previous-step.outputs.parameter.some-parameter}} == "some-value"'
)
```

And

```py
run_script(
    ...,
    when=f'{previous_step.result} == "some-value"'
)
```

is equivalent to

```py
run_script(
    ...,
    when='{{steps.previous-step.outputs.result}} == "some-value"'
)
```

## Complex `when` Clauses

If you want to use more complex `when` clauses than simple comparisons, involving Argo expression functions such as
`filter` or `map` or even [sprig functions](http://masterminds.github.io/sprig/), you should check out Hera's
[`expr` module documentation](../expr.md).

## Improved Task Conditionals

When using DAGs, there are many convenience functions we can use:

* `on_success`
* `on_failure`
* `on_error`
* `on_other_result`
* `when_any_succeeded`
* `when_all_failed`
* `on_workflow_status`

These functions (except `on_workflow_status`) are essentially aliases to `Task`'s `next` function, with the `on`
parameter populated with the corrected `TaskResult`, so they can be used to set stricter dependencies than with the
rshift (`>>`) operator.
