# Parallelism Nested

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/parallelism-nested.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Parameter, Step, Steps, Workflow

    with Workflow(
        generate_name="parallelism-nested-",
        entrypoint="parallel-worker",
        arguments=[
            Parameter(name="seq-list", value='["a","b","c","d"]\n'),
            Parameter(name="parallel-list", value="[1,2,3,4]\n"),
        ],
    ) as w:
        one_job = Container(
            name="one-job",
            image="alpine",
            command=["/bin/sh", "-c"],
            args=["echo {{inputs.parameters.parallel-id}} {{inputs.parameters.seq-id}}; sleep 10"],
            inputs=[Parameter(name="seq-id"), Parameter(name="parallel-id")],
        )

        with Steps(
            name="seq-worker", parallelism=1, inputs=[Parameter(name="seq-list"), Parameter(name="parallel-id")]
        ) as seq_worker:
            with seq_worker.parallel():
                one_job(
                    name="seq-step",
                    arguments=[
                        seq_worker.get_parameter("parallel-id"),
                        Parameter(name="seq-id", value="{{item}}"),
                    ],
                    with_param=seq_worker.get_parameter("seq-list"),
                )

        with Steps(
            name="parallel-worker", inputs=[Parameter(name="seq-list"), Parameter(name="parallel-list")]
        ) as parallel_worker:
            Step(
                name="parallel-worker",
                template=seq_worker,
                arguments=[
                    seq_worker.get_parameter("seq-list"),
                    Parameter(name="parallel-id", value="{{item}}"),
                ],
                with_param=parallel_worker.get_parameter("parallel-list"),
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: parallelism-nested-
    spec:
      entrypoint: parallel-worker
      templates:
      - name: one-job
        container:
          image: alpine
          args:
          - echo {{inputs.parameters.parallel-id}} {{inputs.parameters.seq-id}}; sleep
            10
          command:
          - /bin/sh
          - -c
        inputs:
          parameters:
          - name: seq-id
          - name: parallel-id
      - name: seq-worker
        parallelism: 1
        steps:
        - - name: seq-step
            template: one-job
            withParam: '{{inputs.parameters.seq-list}}'
            arguments:
              parameters:
              - name: parallel-id
                value: '{{inputs.parameters.parallel-id}}'
              - name: seq-id
                value: '{{item}}'
        inputs:
          parameters:
          - name: seq-list
          - name: parallel-id
      - name: parallel-worker
        steps:
        - - name: parallel-worker
            template: seq-worker
            withParam: '{{inputs.parameters.parallel-list}}'
            arguments:
              parameters:
              - name: seq-list
                value: '{{inputs.parameters.seq-list}}'
              - name: parallel-id
                value: '{{item}}'
        inputs:
          parameters:
          - name: seq-list
          - name: parallel-list
      arguments:
        parameters:
        - name: seq-list
          value: |
            ["a","b","c","d"]
        - name: parallel-list
          value: |
            [1,2,3,4]
    ```

