# Steps Inline Workflow

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow

    container = Container(image="argoproj/argosay:v2")

    with Workflow(
        generate_name="steps-inline-",
        entrypoint="main",
        annotations={
            "workflows.argoproj.io/description": ("This workflow demonstrates running a steps with inline templates."),
            "workflows.argoproj.io/version": ">= 3.2.0",
        },
    ) as w:
        with Steps(name="main"):
            Step(name="a", inline=container)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      annotations:
        workflows.argoproj.io/description: This workflow demonstrates running a steps
          with inline templates.
        workflows.argoproj.io/version: '>= 3.2.0'
      generateName: steps-inline-
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - inline:
              container:
                image: argoproj/argosay:v2
            name: a
    ```

