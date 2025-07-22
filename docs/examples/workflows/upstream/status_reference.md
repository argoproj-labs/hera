# Status Reference

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/status-reference.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import ContinueOn

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="status-reference-",
        entrypoint="status-reference",
    ) as w:
        with Steps(
            name="status-reference",
        ) as invocator:
            Step(
                name="flakey-container",
                continue_on=ContinueOn(
                    failed=True,
                ),
                template="flakey-container",
            )
            with invocator.parallel():
                Step(
                    name="failed",
                    template="failed",
                    when="{{steps.flakey-container.status}} == Failed",
                )
                Step(
                    name="succeeded",
                    template="succeeded",
                    when="{{steps.flakey-container.status}} == Succeeded",
                )
        Container(
            name="flakey-container",
            args=["exit 1"],
            command=["sh", "-c"],
            image="alpine:3.6",
        )
        Container(
            name="failed",
            args=['echo "the flakey container failed"'],
            command=["sh", "-c"],
            image="alpine:3.6",
        )
        Container(
            name="succeeded",
            args=['echo "the flakey container passed"'],
            command=["sh", "-c"],
            image="alpine:3.6",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: status-reference-
    spec:
      entrypoint: status-reference
      templates:
      - name: status-reference
        steps:
        - - name: flakey-container
            template: flakey-container
            continueOn:
              failed: true
        - - name: failed
            template: failed
            when: '{{steps.flakey-container.status}} == Failed'
          - name: succeeded
            template: succeeded
            when: '{{steps.flakey-container.status}} == Succeeded'
      - name: flakey-container
        container:
          image: alpine:3.6
          args:
          - exit 1
          command:
          - sh
          - -c
      - name: failed
        container:
          image: alpine:3.6
          args:
          - echo "the flakey container failed"
          command:
          - sh
          - -c
      - name: succeeded
        container:
          image: alpine:3.6
          args:
          - echo "the flakey container passed"
          command:
          - sh
          - -c
    ```

