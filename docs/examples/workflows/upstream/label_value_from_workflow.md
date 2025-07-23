# Label Value From Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/label-value-from-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import Arguments, LabelValueFrom, Parameter, WorkflowMetadata

    with Workflow(
        arguments=Arguments(
            parameters=[
                Parameter(
                    name="foo",
                    value="bar",
                )
            ],
        ),
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/version": ">= v3.3.0",
            "workflows.argoproj.io/description": "This examples show you how to add labels based on an expression.\nYou can then query workflows based on the parameters they were invoked with.\nIn this specific case, the value of foo will set as a label on the workflow.\n",
        },
        generate_name="label-value-from-",
        entrypoint="main",
        workflow_metadata=WorkflowMetadata(
            labels_from={
                "foo": LabelValueFrom(
                    expression="workflow.parameters.foo",
                )
            },
        ),
    ) as w:
        Container(
            name="main",
            image="argoproj/argosay:v2",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: label-value-from-
      annotations:
        workflows.argoproj.io/description: |
          This examples show you how to add labels based on an expression.
          You can then query workflows based on the parameters they were invoked with.
          In this specific case, the value of foo will set as a label on the workflow.
        workflows.argoproj.io/version: '>= v3.3.0'
    spec:
      entrypoint: main
      templates:
      - name: main
        container:
          image: argoproj/argosay:v2
      arguments:
        parameters:
        - name: foo
          value: bar
      workflowMetadata:
        labelsFrom:
          foo:
            expression: workflow.parameters.foo
    ```

