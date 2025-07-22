# Pod Gc Strategy With Label Selector

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/pod-gc-strategy-with-label-selector.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Step, Steps, Workflow
    from hera.workflows.models import LabelSelector, PodGC

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="pod-gc-strategy-with-label-selector-",
        entrypoint="pod-gc-strategy-with-label-selector",
        pod_gc=PodGC(
            delete_delay_duration="30s",
            label_selector=LabelSelector(
                match_labels={"should-be-deleted": "true"},
            ),
            strategy="OnPodSuccess",
        ),
    ) as w:
        with Steps(
            name="pod-gc-strategy-with-label-selector",
        ) as invocator:
            with invocator.parallel():
                Step(
                    name="fail",
                    template="fail",
                )
                Step(
                    name="succeed-deleted",
                    template="succeed-deleted",
                )
                Step(
                    name="succeed-not-deleted",
                    template="succeed-not-deleted",
                )
        Container(
            labels={"should-be-deleted": "true"},
            name="fail",
            args=["exit 1"],
            command=["sh", "-c"],
            image="alpine:3.7",
        )
        Container(
            labels={"should-be-deleted": "true"},
            name="succeed-deleted",
            args=["exit 0"],
            command=["sh", "-c"],
            image="alpine:3.7",
        )
        Container(
            labels={"should-be-deleted": "false"},
            name="succeed-not-deleted",
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
      generateName: pod-gc-strategy-with-label-selector-
    spec:
      entrypoint: pod-gc-strategy-with-label-selector
      templates:
      - name: pod-gc-strategy-with-label-selector
        steps:
        - - name: fail
            template: fail
          - name: succeed-deleted
            template: succeed-deleted
          - name: succeed-not-deleted
            template: succeed-not-deleted
      - name: fail
        container:
          image: alpine:3.7
          args:
          - exit 1
          command:
          - sh
          - -c
        metadata:
          labels:
            should-be-deleted: 'true'
      - name: succeed-deleted
        container:
          image: alpine:3.7
          args:
          - exit 0
          command:
          - sh
          - -c
        metadata:
          labels:
            should-be-deleted: 'true'
      - name: succeed-not-deleted
        container:
          image: alpine:3.7
          args:
          - exit 0
          command:
          - sh
          - -c
        metadata:
          labels:
            should-be-deleted: 'false'
      podGC:
        deleteDelayDuration: 30s
        strategy: OnPodSuccess
        labelSelector:
          matchLabels:
            should-be-deleted: 'true'
    ```

