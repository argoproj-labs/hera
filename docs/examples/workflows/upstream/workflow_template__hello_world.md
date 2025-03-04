# Workflow Template  Hello World

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-template/hello-world.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Step, Steps, Workflow
    from hera.workflows.models import TemplateRef

    with Workflow(
        generate_name="workflow-template-hello-world-",
        entrypoint="hello-world-from-templateRef",
    ) as w:
        print_message_template_ref = TemplateRef(
            name="workflow-template-print-message",
            template="print-message",
        )
        with Steps(name="hello-world-from-templateRef"):
            Step(
                name="call-print-message",
                template_ref=print_message_template_ref,
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
      entrypoint: hello-world-from-templateRef
      templates:
      - name: hello-world-from-templateRef
        steps:
        - - name: call-print-message
            arguments:
              parameters:
              - name: message
                value: hello world
            templateRef:
              name: workflow-template-print-message
              template: print-message
    ```

