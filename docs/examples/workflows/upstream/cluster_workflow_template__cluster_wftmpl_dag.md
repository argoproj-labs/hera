# Cluster Workflow Template  Cluster Wftmpl Dag

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/cluster-workflow-template/cluster-wftmpl-dag.yaml).




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
                    name="cluster-workflow-template-whalesay-template", template="whalesay-template", cluster_scope=True
                ),
                arguments=Parameter(name="message", value="A"),
            )
            B = Task(
                name="B",
                template_ref=m.TemplateRef(
                    name="cluster-workflow-template-whalesay-template", template="whalesay-template", cluster_scope=True
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
                    name="cluster-workflow-template-whalesay-template", template="whalesay-template", cluster_scope=True
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
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: message
                value: A
            name: A
            templateRef:
              clusterScope: true
              name: cluster-workflow-template-whalesay-template
              template: whalesay-template
          - arguments:
              parameters:
              - name: message
                value: B
            depends: A
            name: B
            templateRef:
              clusterScope: true
              name: cluster-workflow-template-whalesay-template
              template: whalesay-template
          - depends: A
            name: C
            templateRef:
              clusterScope: true
              name: cluster-workflow-template-inner-dag
              template: inner-diamond
          - arguments:
              parameters:
              - name: message
                value: D
            depends: B && C
            name: D
            templateRef:
              clusterScope: true
              name: cluster-workflow-template-whalesay-template
              template: whalesay-template
        name: diamond
    ```

