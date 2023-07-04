# Cluster Workflow Template  Mixed Cluster Namespaced Wftmpl Steps

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Parameter,
        Step,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="workflow-template-steps-", entrypoint="hello-hello-hello") as w:
        with Steps(name="hello-hello-hello") as s:
            Step(
                name="hello1",
                template_ref=m.TemplateRef(
                    name="workflow-template-whalesay-template",
                    template="whalesay-template",
                ),
                arguments=Parameter(name="message", value="hello1"),
            )
            with s.parallel():
                Step(
                    name="hello2a",
                    template_ref=m.TemplateRef(
                        name="cluster-workflow-template-inner-steps",
                        template="inner-steps",
                        cluster_scope=True,
                    ),
                    arguments=Parameter(name="message", value="hello2a"),
                )
                Step(
                    name="hello2b",
                    template_ref=m.TemplateRef(
                        name="workflow-template-whalesay-template",
                        template="whalesay-template",
                    ),
                    arguments=Parameter(name="message", value="hello2b"),
                )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-template-steps-
    spec:
      entrypoint: hello-hello-hello
      templates:
      - name: hello-hello-hello
        steps:
        - - arguments:
              parameters:
              - name: message
                value: hello1
            name: hello1
            templateRef:
              name: workflow-template-whalesay-template
              template: whalesay-template
        - - arguments:
              parameters:
              - name: message
                value: hello2a
            name: hello2a
            templateRef:
              clusterScope: true
              name: cluster-workflow-template-inner-steps
              template: inner-steps
          - arguments:
              parameters:
              - name: message
                value: hello2b
            name: hello2b
            templateRef:
              name: workflow-template-whalesay-template
              template: whalesay-template
    ```

