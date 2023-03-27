# Introduction

Hera is a Python library that allows you to construct and submit Argo Workflows. It is designed to be intuitive and easy to use, while also providing a powerful interface to the underlying Argo API.

## Hera V5 vs V4

Hera v5 is a major release that introduces breaking changes from v4. The main reason for this is that v5 is a complete rewrite of the library, and is now based on the OpenAPI specification of Argo Workflows.

This allows us to provide a more intuitive interface to the Argo API, while also providing full feature parity with Argo Workflows. This means that you can now use all the features of Argo Workflows in your workflows.

In addition, the codebase is now much more readable, and the focus can be fully dedicated to improving user workflows.

The library is divided into two main components:

- `hera.workflows.models` - This package contains the auto-generated code that allows you to construct Argo Workflows. It provides Pydantic models for all the Argo Workflows OpenAPI objects, and allows you to construct workflows using these models. These models are based on the OpenAPI specification, and are therefore exactly the same as the models used by Argo Workflows.

- `hera.workflows` - This package contains the hand-written code that allows you to construct and submit Argo Workflows. It wraps the auto-generated code, and provides a more intuitive interface to the Argo API. It also provides a number of useful features, such as the ability to submit workflows from a Python function. This package has various extension points that allow you to plug-in the auto-generated models in case you need to use a feature that is not yet supported by the hand-written code.

The major differences between v4 and v5 are:

- The `hera.workflows.models` package is now auto-generated, and is based on the OpenAPI specification of Argo Workflows. This means that all the models are exactly the same as the models used by Argo Workflows, and you can use all the features of Argo Workflows in your workflows written with `hera`.

- The auto-generated models are based on Pydantic, which means that you can use all the features of Pydantic to construct your workflows. This includes better type-checking, auto-completion in IDEs and more. 

- All template types are now supported. This means that you can now use all the template types that are supported by Argo Workflows, such as DAGs, Steps, Suspend and more. Previously, only the DAG template type was supported.

- The hand-written code has been rewritten to be extensible. This means that you can now easily extend the library to support new features, or to support features that are not yet supported by the hand-written code. This is done by using the `hera.workflows.models` package, and plugging it into the `hera.workflows` package.

The following example shows how to use the DAG template type.

```python
from hera.workflows import (
    DAG,
    Workflow,
    script,
)


# Notice that we are using the script decorator to define the function.
# This is required in order to use the function as a template.
# The decorator also allows us to define the image that will be used to run the function and
# other parameters that are specific to the Script template type.
@script(add_cwd_to_sys_path=False, image="python:alpine3.6")
def say(message):
    print(message)


with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    # Note that we need to explicitly specify the DAG template type.
    with DAG(name="diamond"):
        # We can now use the decorated function as tasks in the DAG.
        A = say(name="A", arguments={"message": "A"})
        B = say(name="B", arguments={"message": "B"})
        C = say(name="C", arguments={"message": "C"})
        D = say(name="D", arguments={"message": "D"})
        # We can also use the `>>` operator to define dependencies between tasks.
        A >> [B, C] >> D
```
