# Pod Gc Strategy

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-gc-strategy.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import PodGC

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="pod-gc-strategy-",
        entrypoint="pod-gc-strategy",
        pod_gc=PodGC(
            delete_delay_duration="30s",
            strategy="OnPodSuccess",
        ),
    ) as w:
        with Steps(
            name="pod-gc-strategy",
        ) as invocator:
            with invocator.parallel():
                Step(
                    name="fail",
                    template="fail",
                )
                Step(
                    name="succeed",
                    template="succeed",
                )
        Container(
            name="fail",
            args=["exit 1"],
            command=["sh", "-c"],
            image="alpine:3.7",
        )
        Container(
            name="succeed",
            args=["exit 0"],
            command=["sh", "-c"],
            image="alpine:3.7",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: pod-gc-strategy-
    spec:
      entrypoint: pod-gc-strategy
      templates:
      - name: pod-gc-strategy
        steps:
        - - name: fail
            template: fail
          - name: succeed
            template: succeed
      - name: fail
        container:
          image: alpine:3.7
          args:
          - exit 1
          command:
          - sh
          - -c
      - name: succeed
        container:
          image: alpine:3.7
          args:
          - exit 0
          command:
          - sh
          - -c
      podGC:
        deleteDelayDuration: 30s
        strategy: OnPodSuccess
    ```

