# Dag Enhanced Depends

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Workflow

    with Workflow(
        generate_name="dag-diamond-",
        entrypoint="diamond",
    ) as w:
        pass_ = Container(
            name="pass",
            image="alpine:3.7",
            command=["sh", "-c", "exit 0"],
        )
        fail = Container(
            name="fail",
            image="alpine:3.7",
            command=["sh", "-c", "exit 1"],
        )
        with DAG(name="diamond"):
            A = pass_(name="A")
            B = pass_(name="B")
            C = fail(name="C")
            should_execute_1 = pass_(name="should-execute-1", depends="A && (C.Succeeded || C.Failed)")
            should_execute_2 = pass_(name="should-execute-2", depends="B || C")
            should_not_execute = pass_(name="should-not-execute", depends="B && C")
            should_execute_3 = pass_(name="should-execute-3", depends="should-execute-2.Succeeded || should-not-execute")

            A >> [B, C]
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - container:
          command:
          - sh
          - -c
          - exit 0
          image: alpine:3.7
        name: pass
      - container:
          command:
          - sh
          - -c
          - exit 1
          image: alpine:3.7
        name: fail
      - dag:
          tasks:
          - name: A
            template: pass
          - depends: A
            name: B
            template: pass
          - depends: A
            name: C
            template: fail
          - depends: A && (C.Succeeded || C.Failed)
            name: should-execute-1
            template: pass
          - depends: B || C
            name: should-execute-2
            template: pass
          - depends: B && C
            name: should-not-execute
            template: pass
          - depends: should-execute-2.Succeeded || should-not-execute
            name: should-execute-3
            template: pass
        name: diamond
    ```

