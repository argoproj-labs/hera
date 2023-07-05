# Workflow Template  Hello World

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/workflow-template/hello-world.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Step, Steps, Workflow
    from hera.workflows.models import TemplateRef

    with Workflow(
        generate_name="workflow-template-hello-world-",
        entrypoint="whalesay",
    ) as w:
        whalesay_template_ref = TemplateRef(
            name="workflow-template-whalesay-template",
            template="whalesay-template",
        )
        with Steps(name="whalesay"):
            Step(
                name="call-whalesay-template",
                template_ref=whalesay_template_ref,
                arguments={"message": "hello world"},
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-template-hello-world-
    spec:
      entrypoint: whalesay
      templates:
      - name: whalesay
        steps:
        - - arguments:
              parameters:
              - name: message
                value: hello world
            name: call-whalesay-template
            templateRef:
              name: workflow-template-whalesay-template
              template: whalesay-template
    ```

