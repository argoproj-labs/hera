# Cluster Workflow Template  Cluster Wftmpl Dag

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/cluster-workflow-template/cluster-wftmpl-dag.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        Parameter,
        Task,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="workflow-template-dag-diamond-", entrypoint="diamond") as w:
        with DAG(name="diamond") as dag:
            A = Task(
                name="A",
                template_ref=m.TemplateRef(
                    name="cluster-workflow-template-print-message", template="print-message", cluster_scope=True
                ),
                arguments=Parameter(name="message", value="A"),
            )
            B = Task(
                name="B",
                template_ref=m.TemplateRef(
                    name="cluster-workflow-template-print-message", template="print-message", cluster_scope=True
                ),
                arguments=Parameter(name="message", value="B"),
            )
            C = Task(
                name="C",
                template_ref=m.TemplateRef(
                    name="cluster-workflow-template-inner-dag", template="inner-diamond", cluster_scope=True
                ),
            )
            D = Task(
                name="D",
                template_ref=m.TemplateRef(
                    name="cluster-workflow-template-print-message", template="print-message", cluster_scope=True
                ),
                arguments=Parameter(name="message", value="D"),
            )
            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-template-dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - name: diamond
        dag:
          tasks:
          - name: A
            arguments:
              parameters:
              - name: message
                value: A
            templateRef:
              name: cluster-workflow-template-print-message
              clusterScope: true
              template: print-message
          - name: B
            depends: A
            arguments:
              parameters:
              - name: message
                value: B
            templateRef:
              name: cluster-workflow-template-print-message
              clusterScope: true
              template: print-message
          - name: C
            depends: A
            templateRef:
              name: cluster-workflow-template-inner-dag
              clusterScope: true
              template: inner-diamond
          - name: D
            depends: B && C
            arguments:
              parameters:
              - name: message
                value: D
            templateRef:
              name: cluster-workflow-template-print-message
              clusterScope: true
              template: print-message
    ```

