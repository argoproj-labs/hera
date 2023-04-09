# Workflow Template  Workflow Template Ref With Entrypoint Arg Passing

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-template/workflow-template-ref-with-entrypoint-arg-passing.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Parameter,
        Workflow,
        models as m,
    )

    w = Workflow(
        generate_name="workflow-template-hello-world-",
        entrypoint="whalesay-template",
        workflow_template_ref=m.WorkflowTemplateRef(
            name="workflow-template-whalesay-template",
        ),
        arguments=Parameter(name="message", value="hello world"),
    )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-template-hello-world-
    spec:
      arguments:
        parameters:
        - name: message
          value: hello world
      entrypoint: whalesay-template
      workflowTemplateRef:
        name: workflow-template-whalesay-template
    ```

