# Dag Continue On Fail

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-continue-on-fail.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Task, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="dag-contiue-on-fail-",
        entrypoint="workflow",
    ) as w:
        with DAG(
            name="workflow",
        ) as invocator:
            Task(
                name="A",
                template="hello-world",
            )
            Task(
                name="B",
                template="intentional-fail",
                depends="A",
            )
            Task(
                name="C",
                template="hello-world",
                depends="A",
            )
            Task(
                name="D",
                template="hello-world",
                depends="B.Failed && C",
            )
            Task(
                name="E",
                template="intentional-fail",
                depends="A",
            )
            Task(
                name="F",
                template="hello-world",
                depends="A",
            )
            Task(
                name="G",
                template="hello-world",
                depends="E && F",
            )
        Container(
            name="hello-world",
            args=["hello world"],
            command=["echo"],
            image="busybox",
        )
        Container(
            name="intentional-fail",
            args=["echo intentional failure; exit 1"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-contiue-on-fail-
    spec:
      entrypoint: workflow
      templates:
      - name: workflow
        dag:
          tasks:
          - name: A
            template: hello-world
          - name: B
            depends: A
            template: intentional-fail
          - name: C
            depends: A
            template: hello-world
          - name: D
            depends: B.Failed && C
            template: hello-world
          - name: E
            depends: A
            template: intentional-fail
          - name: F
            depends: A
            template: hello-world
          - name: G
            depends: E && F
            template: hello-world
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      - name: intentional-fail
        container:
          image: alpine:latest
          args:
          - echo intentional failure; exit 1
          command:
          - sh
          - -c
    ```

