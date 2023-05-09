# Dag Nested

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-nested.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    echo = Container(
        name="echo",
        inputs=Parameter(name="message"),
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
    )

    with Workflow(generate_name="dag-nested-", entrypoint="diamond") as w:
        with DAG(name="nested-diamond", inputs=[Parameter(name="message")]) as nested_diamond:
            A = echo(name="A", arguments={"message": "{{inputs.parameters.message}}A"})
            B = echo(name="B", arguments={"message": "{{inputs.parameters.message}}B"})
            C = echo(name="C", arguments={"message": "{{inputs.parameters.message}}C"})
            D = echo(name="D", arguments={"message": "{{inputs.parameters.message}}D"})
            A >> [B, C] >> D

        with DAG(name="diamond") as diamond:
            A = nested_diamond(name="A", arguments={"message": "A"})
            B = nested_diamond(name="B", arguments={"message": "B"})
            C = nested_diamond(name="C", arguments={"message": "C"})
            D = nested_diamond(name="D", arguments={"message": "D"})
            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-nested-
    spec:
      entrypoint: diamond
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: message
                value: '{{inputs.parameters.message}}A'
            name: A
            template: echo
          - arguments:
              parameters:
              - name: message
                value: '{{inputs.parameters.message}}B'
            depends: A
            name: B
            template: echo
          - arguments:
              parameters:
              - name: message
                value: '{{inputs.parameters.message}}C'
            depends: A
            name: C
            template: echo
          - arguments:
              parameters:
              - name: message
                value: '{{inputs.parameters.message}}D'
            depends: B && C
            name: D
            template: echo
        inputs:
          parameters:
          - name: message
        name: nested-diamond
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
            template: nested-diamond
          - arguments:
              parameters:
              - name: message
                value: B
            depends: A
            name: B
            template: nested-diamond
          - arguments:
              parameters:
              - name: message
                value: C
            depends: A
            name: C
            template: nested-diamond
          - arguments:
              parameters:
              - name: message
                value: D
            depends: B && C
            name: D
            template: nested-diamond
        name: diamond
    ```

