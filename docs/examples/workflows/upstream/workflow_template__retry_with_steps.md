# Workflow Template  Retry With Steps

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Step,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="workflow-template-retry-with-steps-",
        entrypoint="retry-with-steps",
    ) as w:
        template_ref = m.TemplateRef(name="workflow-template-random-fail-template", template="random-fail-template")
        with Steps(name="retry-with-steps") as s:
            Step(name="hello1", template_ref=template_ref)
            with s.parallel():
                Step(
                    name="hello2a",
                    template_ref=m.TemplateRef(
                        name="workflow-template-random-fail-template",
                        template="random-fail-template",
                    ),
                )
                Step(name="hello2b", template_ref=template_ref)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: workflow-template-retry-with-steps-
    spec:
      entrypoint: retry-with-steps
      templates:
      - name: retry-with-steps
        steps:
        - - name: hello1
            templateRef:
              name: workflow-template-random-fail-template
              template: random-fail-template
        - - name: hello2a
            templateRef:
              name: workflow-template-random-fail-template
              template: random-fail-template
          - name: hello2b
            templateRef:
              name: workflow-template-random-fail-template
              template: random-fail-template
    ```

