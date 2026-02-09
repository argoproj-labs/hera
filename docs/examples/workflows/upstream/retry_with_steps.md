# Retry With Steps

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-with-steps.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import IntOrString, RetryStrategy

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="retry-with-steps-",
        entrypoint="retry-with-steps",
    ) as w:
        with Steps(
            name="retry-with-steps",
        ) as invocator:
            Step(
                name="hello1",
                template="random-fail",
            )
            with invocator.parallel():
                Step(
                    name="hello2a",
                    template="random-fail",
                )
                Step(
                    name="hello2b",
                    template="random-fail",
                )
        Container(
            name="random-fail",
            retry_strategy=RetryStrategy(
                limit=IntOrString(
                    root="10",
                ),
            ),
            args=[
                "import random; import sys; print('retries: {{retries}}'); exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"
            ],
            command=["python", "-c"],
            image="python:alpine3.6",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: retry-with-steps-
    spec:
      entrypoint: retry-with-steps
      templates:
      - name: retry-with-steps
        steps:
        - - name: hello1
            template: random-fail
        - - name: hello2a
            template: random-fail
          - name: hello2b
            template: random-fail
      - name: random-fail
        container:
          image: python:alpine3.6
          args:
          - 'import random; import sys; print(''retries: {{retries}}''); exit_code = random.choice([0,
            1, 1]); sys.exit(exit_code)'
          command:
          - python
          - -c
        retryStrategy:
          limit: '10'
    ```

