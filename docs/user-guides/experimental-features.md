# Experimental Features

From time to time, Hera will release a new feature under the "experimental feature" flag while we develop the feature
and ensure stability. Once the feature is stable and we have decided to support it long-term, it will "graduate" into
a fully-supported feature.

To enable experimental features you must set the feature by name to `True` in the `global_config.experimental_features`
dictionary before using the feature:

```py
global_config.experimental_features["NAME_OF_FEATURE"] = True
```

Note that experimental features are subject to breaking changes in future releases of the same major version. We will
usually announce changes in [the Hera slack channel](https://cloud-native.slack.com/archives/C03NRMD9KPY).

## Currently supported experimental features:

### Script IO Models

Hera provides Pydantic models for you to create subclasses from, which allow you to more easily declare script template
inputs. Any fields that you declare in your subclass of `Input` will become input parameters or artifacts, while
`Output` fields will become output parameters artifacts. The fields that you declare can be `Annotated` as a `Parameter`
or `Artifact`, as any fields with a basic type will become `Parameters`. Turning on the `script_pydantic_io` flag will
automatically enable the `script_annotations` experimental feature.

To enable Hera input/output models, you must set the `experimental_feature` flag `script_pydantic_io`

```py
global_config.experimental_features["script_pydantic_io"] = True
```

Read the full guide on script pydantic IO in [the script user guide](../user-guides/script-runner-io.md).

## Graduated features

Once an experimental feature is robust and reliable, we "graduate" them to allow their use without setting the
`experimental_features` flag of the `global_config`. This comes with better support and guarantees for their feature
set. We list graduated features here so you can keep up to date.

### `RunnerScriptConstructor` (since 5.10)

The `RunnerScriptConstructor` found in `hera.workflows.script` and seen in the
[typed script IO example](../examples/workflows/hera-runner/typed_script_input_output.md) is a robust way to run Python functions
on Argo. The image used by the script should be built from the source code package itself and its dependencies, so that
the source code's functions, dependencies, and Hera itself are available to run. The `RunnerScriptConstructor` is also
compatible with Pydantic so supports deserializing inputs to Python objects and serializing outputs to json strings.

Read [the Runner Script Guide](script-constructors.md#runner-scripts) to learn more!

### Script Annotations (since 5.19)

Annotation syntax using `typing.Annotated` is supported for `Parameter`s and `Artifact`s as inputs and outputs for
functions decorated as `scripts`. They use `Annotated` as the type in the function parameters and allow us to simplify
writing scripts with parameters and artifacts that require additional fields such as a `description` or alternative
`name`.

Read the full guide on script annotations in [the script user guide](../user-guides/script-annotations.md).

## Retired features

These features have been retired and are no longer supported.

### Decorators for main template types

Decorators for dags, steps and containers are provided alongside a new script decorator, letting your declare Workflows via Python functions alone.
The maintainers felt it would be better to focus on one fully-supported syntax instead of continuing support for a second, less-supported syntax.

Read the full guide on decorators in [the decorator user guide](../user-guides/retired/decorators.md).
