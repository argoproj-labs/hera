# Loops Dag

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/loops-dag.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    with Workflow(
        generate_name="loops-dag-",
        entrypoint="loops-dag",
    ) as w:
        echo = Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay"],
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
          - cowsay
          image: docker/whalesay:latest
        inputs:
          parameters:
          - name: message
        name: whalesay
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: message
                value: A
            name: A
            template: whalesay
          - arguments:
              parameters:
              - name: message
                value: '{{item}}'
            depends: A
            name: B
            template: whalesay
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
            template: whalesay
        name: loops-dag
    ```

