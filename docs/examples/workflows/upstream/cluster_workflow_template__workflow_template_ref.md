# Cluster Workflow Template  Workflow Template Ref

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/cluster-workflow-template/workflow-template-ref.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow
    from hera.workflows.models import WorkflowTemplateRef

    wt_ref = WorkflowTemplateRef(name="cluster-workflow-template-submittable", cluster_scope=True)

    w = Workflow(
        generate_name="cluster-workflow-template-hello-world-",
        workflow_template_ref=wt_ref,
    )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: cluster-workflow-template-hello-world-
    spec:
      workflowTemplateRef:
        clusterScope: true
        name: cluster-workflow-template-submittable
    ```

