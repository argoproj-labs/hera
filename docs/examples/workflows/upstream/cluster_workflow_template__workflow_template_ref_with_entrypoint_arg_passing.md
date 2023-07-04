# Cluster Workflow Template  Workflow Template Ref With Entrypoint Arg Passing

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Parameter,
        Workflow,
        models as m,
    )

    w = Workflow(
        generate_name="cluster-workflow-template-hello-world-",
        entrypoint="whalesay-template",
        arguments=Parameter(name="message", value="hello world"),
        workflow_template_ref=m.WorkflowTemplateRef(
            name="cluster-workflow-template-whalesay-template",
            cluster_scope=True,
        ),
    )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: cluster-workflow-template-hello-world-
    spec:
      arguments:
        parameters:
        - name: message
          value: hello world
      entrypoint: whalesay-template
      workflowTemplateRef:
        clusterScope: true
        name: cluster-workflow-template-whalesay-template
    ```

