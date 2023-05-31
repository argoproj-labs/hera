# Dag Diamond

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-diamond.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    with Workflow(
        generate_name="dag-diamond-",
        entrypoint="diamond",
    ) as w:
        echo = Container(
            name="echo",
            image="alpine:3.7",
            command=["echo", "{{inputs.parameters.message}}"],
            inputs=[Parameter(name="message")],
        )
        with DAG(name="diamond"):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "B"})
            C = echo(name="C", arguments={"message": "C"})
            D = echo(name="D", arguments={"message": "D"})
            A >> [B, C] >> D
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
          - echo
          - '{{inputs.parameters.message}}'
          image: alpine:3.7
        inputs:
          parameters:
          - name: message
        name: echo
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: message
                value: A
            name: A
            template: echo
          - arguments:
              parameters:
              - name: message
                value: B
            depends: A
            name: B
            template: echo
          - arguments:
              parameters:
              - name: message
                value: C
            depends: A
            name: C
            template: echo
          - arguments:
              parameters:
              - name: message
                value: D
            depends: B && C
            name: D
            template: echo
        name: diamond
    ```

