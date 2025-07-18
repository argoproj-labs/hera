# Dag Diamond With Container



This is the canonical "diamond" example, but using a `Container`.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        DAG,
        Container,
        Parameter,
        Workflow,
    )

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
      - name: echo
        container:
          image: alpine:3.7
          command:
          - echo
          - '{{inputs.parameters.message}}'
        inputs:
          parameters:
          - name: message
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
    ```

