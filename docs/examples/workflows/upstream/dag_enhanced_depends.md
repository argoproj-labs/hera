# Dag Enhanced Depends

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-enhanced-depends.yaml).




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
      - name: pass
        container:
          image: alpine:3.7
          command:
          - sh
          - -c
          - exit 0
      - name: fail
        container:
          image: alpine:3.7
          command:
          - sh
          - -c
          - exit 1
      - name: diamond
        dag:
          tasks:
          - name: A
            template: pass
          - name: B
            depends: A
            template: pass
          - name: C
            depends: A
            template: fail
          - name: should-execute-1
            depends: A && (C.Succeeded || C.Failed)
            template: pass
          - name: should-execute-2
            depends: B || C
            template: pass
          - name: should-not-execute
            depends: B && C
            template: pass
          - name: should-execute-3
            depends: should-execute-2.Succeeded || should-not-execute
            template: pass
    ```

