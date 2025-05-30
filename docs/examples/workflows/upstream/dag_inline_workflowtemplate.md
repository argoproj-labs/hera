# Dag Inline Workflowtemplate

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-inline-workflowtemplate.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Task, WorkflowTemplate

    container = Container(image="argoproj/argosay:v2")

    with WorkflowTemplate(
        name="dag-inline",
        entrypoint="main",
        annotations={
            "workflows.argoproj.io/description": ("This example demonstrates running a DAG with inline templates."),
            "workflows.argoproj.io/version": ">= 3.2.0",
        },
    ) as w:
        with DAG(name="main"):
            Task(name="a", inline=container)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: dag-inline
      annotations:
        workflows.argoproj.io/description: This example demonstrates running a DAG with
          inline templates.
        workflows.argoproj.io/version: '>= 3.2.0'
    spec:
      entrypoint: main
      templates:
      - name: main
        dag:
          tasks:
          - name: a
            inline:
              container:
                image: argoproj/argosay:v2
    ```

