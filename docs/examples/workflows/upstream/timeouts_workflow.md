# Timeouts Workflow

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Steps, Workflow

    with Workflow(generate_name="timeouts-workflow-", entrypoint="bunch-of-sleeps", active_deadline_seconds=30) as w:
        sleep = Container(
            name="sleep",
            image="debian:9.5-slim",
            command=["sleep", "1d"],
        )
        unschedule = Container(
            name="unschedulable",
            image="alpine:latest",
            node_selector={"beta.kubernetes.io/arch": "no-such-arch"},
        )
        with Steps(name="bunch-of-sleeps") as s:
            with s.parallel():
                sleep(name="sleep-one-day", with_items=[1, 2, 3])
                unschedule(with_items=[1, 2, 3])
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: timeouts-workflow-
    spec:
      activeDeadlineSeconds: 30
      entrypoint: bunch-of-sleeps
      templates:
      - container:
          command:
          - sleep
          - 1d
          image: debian:9.5-slim
        name: sleep
      - container:
          image: alpine:latest
        name: unschedulable
        nodeSelector:
          beta.kubernetes.io/arch: no-such-arch
      - name: bunch-of-sleeps
        steps:
        - - name: sleep-one-day
            template: sleep
            withItems:
            - 1
            - 2
            - 3
          - name: unschedulable
            template: unschedulable
            withItems:
            - 1
            - 2
            - 3
    ```

