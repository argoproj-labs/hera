# Steps Daemon Retry Strategy

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/steps-daemon-retry-strategy.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import (
        Arguments,
        HTTPGetAction,
        Inputs,
        IntOrString,
        Mutex,
        Parameter,
        Probe,
        RetryStrategy,
        Sequence,
        Synchronization,
    )

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="steps-daemon-retry-",
        entrypoint="main",
    ) as w:
        with Steps(
            name="main",
        ) as invocator:
            Step(
                name="server",
                template="server",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="server-ip",
                            value="{{steps.server.ip}}",
                        )
                    ],
                ),
                name="client",
                template="client",
                with_sequence=Sequence(
                    count=IntOrString(
                        root="10",
                    ),
                ),
            )
        Container(
            daemon=True,
            name="server",
            retry_strategy=RetryStrategy(
                limit=IntOrString(
                    root="10",
                ),
            ),
            args=["-g", "daemon off;"],
            command=["nginx"],
            image="nginx:latest",
            readiness_probe=Probe(
                http_get=HTTPGetAction(
                    path="/",
                    port=80,
                ),
                initial_delay_seconds=2,
                timeout_seconds=1,
            ),
        )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="server-ip",
                    )
                ],
            ),
            name="client",
            synchronization=Synchronization(
                mutex=Mutex(
                    name="client-{{workflow.uid}}",
                ),
            ),
            args=[
                "echo curl --silent -G http://{{inputs.parameters.server-ip}}:80/ && curl --silent -G http://{{inputs.parameters.server-ip}}:80/"
            ],
            command=["/bin/sh", "-c"],
            image="appropriate/curl:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: steps-daemon-retry-
    spec:
      entrypoint: main
      templates:
      - name: main
        steps:
        - - name: server
            template: server
        - - name: client
            template: client
            arguments:
              parameters:
              - name: server-ip
                value: '{{steps.server.ip}}'
            withSequence:
              count: '10'
      - name: server
        daemon: true
        container:
          image: nginx:latest
          args:
          - -g
          - daemon off;
          command:
          - nginx
          readinessProbe:
            initialDelaySeconds: 2
            timeoutSeconds: 1
            httpGet:
              path: /
              port: 80
        retryStrategy:
          limit: '10'
      - name: client
        container:
          image: appropriate/curl:latest
          args:
          - echo curl --silent -G http://{{inputs.parameters.server-ip}}:80/ && curl --silent
            -G http://{{inputs.parameters.server-ip}}:80/
          command:
          - /bin/sh
          - -c
        inputs:
          parameters:
          - name: server-ip
        synchronization:
          mutex:
            name: client-{{workflow.uid}}
    ```

