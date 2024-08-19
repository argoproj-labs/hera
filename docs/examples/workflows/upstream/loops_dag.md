# Loops Dag

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/loops-dag.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    with Workflow(
        generate_name="loops-dag-",
        entrypoint="loops-dag",
    ) as w:
        echo = Container(
            name="print-message",
            image="busybox",
            command=["echo"],
            args=["{{inputs.parameters.message}}"],
            inputs=[Parameter(name="message")],
        )
        with DAG(name="loops-dag"):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "{{item}}"}, with_items=["foo", "bar", "baz"])
            C = echo(name="C", arguments={"message": "C"})
            A >> B >> C
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: loops-dag-
    spec:
      entrypoint: loops-dag
      templates:
      - container:
          args:
          - '{{inputs.parameters.message}}'
          command:
          - echo
          image: busybox
        inputs:
          parameters:
          - name: message
        name: print-message
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: message
                value: A
            name: A
            template: print-message
          - arguments:
              parameters:
              - name: message
                value: '{{item}}'
            depends: A
            name: B
            template: print-message
            withItems:
            - foo
            - bar
            - baz
          - arguments:
              parameters:
              - name: message
                value: C
            depends: B
            name: C
            template: print-message
        name: loops-dag
    ```

