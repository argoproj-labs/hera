# Resubmit

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/resubmit.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Step, Steps, Task, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="resubmit-",
        entrypoint="rand-fail-dag",
    ) as w:
        with DAG(
            name="rand-fail-dag",
        ) as invocator:
            Task(
                name="A",
                template="random-fail",
            )
            Task(
                name="B",
                template="rand-fail-steps",
            )
            Task(
                name="C",
                template="random-fail",
                depends="B",
            )
            Task(
                name="D",
                template="random-fail",
                depends="A && B",
            )
        with Steps(
            name="rand-fail-steps",
        ) as invocator:
            with invocator.parallel():
                Step(
                    name="randfail1a",
                    template="random-fail",
                )
                Step(
                    name="randfail1b",
                    template="random-fail",
                )
            with invocator.parallel():
                Step(
                    name="randfail2a",
                    template="random-fail",
                )
                Step(
                    name="randfail2b",
                    template="random-fail",
                )
                Step(
                    name="randfail2c",
                    template="random-fail",
                )
                Step(
                    name="randfail2d",
                    template="random-fail",
                )
        Container(
            name="random-fail",
            args=[
                "import random; import sys; exit_code = random.choice([0, 0, 1]); print('exiting with code {}'.format(exit_code)); sys.exit(exit_code)"
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
      generateName: resubmit-
    spec:
      entrypoint: rand-fail-dag
      templates:
      - name: rand-fail-dag
        dag:
          tasks:
          - name: A
            template: random-fail
          - name: B
            template: rand-fail-steps
          - name: C
            depends: B
            template: random-fail
          - name: D
            depends: A && B
            template: random-fail
      - name: rand-fail-steps
        steps:
        - - name: randfail1a
            template: random-fail
          - name: randfail1b
            template: random-fail
        - - name: randfail2a
            template: random-fail
          - name: randfail2b
            template: random-fail
          - name: randfail2c
            template: random-fail
          - name: randfail2d
            template: random-fail
      - name: random-fail
        container:
          image: python:alpine3.6
          args:
          - import random; import sys; exit_code = random.choice([0, 0, 1]); print('exiting
            with code {}'.format(exit_code)); sys.exit(exit_code)
          command:
          - python
          - -c
    ```

