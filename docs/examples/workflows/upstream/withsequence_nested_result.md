# Withsequence Nested Result

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/withsequence-nested-result.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Script, Step, Steps, Workflow
    from hera.workflows.models import IntOrString, Sequence

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="withsequence-nested-result-",
        entrypoint="hello-entrypoint",
    ) as w:
        with Steps(
            name="hello-entrypoint",
        ) as invocator:
            Step(
                name="hello-a",
                template="hello",
            )
            Step(
                name="hello-b",
                template="hello-hello",
                with_sequence=Sequence(
                    end=IntOrString(
                        __root__="{{steps.hello-a.outputs.result}}",
                    ),
                    start=IntOrString(
                        __root__="1",
                    ),
                ),
            )
        with Steps(
            name="hello-hello",
        ) as invocator:
            Step(
                name="hello-b",
                template="hello",
            )
            Step(
                name="hello-c",
                template="hello",
                with_sequence=Sequence(
                    end=IntOrString(
                        __root__="{{steps.hello-b.outputs.result}}",
                    ),
                    start=IntOrString(
                        __root__="1",
                    ),
                ),
            )
        Script(
            name="hello",
            command=["python"],
            image="python:alpine3.6",
            source="import random\nresult = random.randint(0,5)\nprint(result)\n",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: withsequence-nested-result-
    spec:
      entrypoint: hello-entrypoint
      templates:
      - name: hello-entrypoint
        steps:
        - - name: hello-a
            template: hello
        - - name: hello-b
            template: hello-hello
            withSequence:
              end: '{{steps.hello-a.outputs.result}}'
              start: '1'
      - name: hello-hello
        steps:
        - - name: hello-b
            template: hello
        - - name: hello-c
            template: hello
            withSequence:
              end: '{{steps.hello-b.outputs.result}}'
              start: '1'
      - name: hello
        script:
          image: python:alpine3.6
          source: |
            import random
            result = random.randint(0,5)
            print(result)
          command:
          - python
    ```

