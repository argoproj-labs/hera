# Template Defaults

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/template-defaults.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import IntOrString, RetryStrategy, Template

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={
            "workflows.argoproj.io/description": "Template defaults will provide the fixability to configure the defaults values for all templates in workflow.\nIndividual template can be overide default values.\n",
            "workflows.argoproj.io/version": ">= 3.1.0",
        },
        generate_name="template-defaults-",
        entrypoint="main",
        template_defaults=Template(
            retry_strategy=RetryStrategy(
                limit=IntOrString(
                    root="2",
                ),
            ),
            timeout="30s",
        ),
    ) as w:
        with Steps(
            name="main",
        ) as invocator:
            Step(
                name="retry-backoff",
                template="retry-backoff",
            )
            Step(
                name="hello-world",
                template="hello-world",
            )
        Container(
            name="hello-world",
            args=["hello world"],
            command=["echo"],
            image="busybox",
        )
        Container(
            name="retry-backoff",
            args=["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"],
            command=["python", "-c"],
            image="python:alpine3.6",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: template-defaults-
      annotations:
        workflows.argoproj.io/description: |
          Template defaults will provide the fixability to configure the defaults values for all templates in workflow.
          Individual template can be overide default values.
        workflows.argoproj.io/version: '>= 3.1.0'
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - name: retry-backoff
            template: retry-backoff
        - - name: hello-world
            template: hello-world
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      - name: retry-backoff
        container:
          image: python:alpine3.6
          args:
          - import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)
          command:
          - python
          - -c
      templateDefaults:
        timeout: 30s
        retryStrategy:
          limit: '2'
    ```

