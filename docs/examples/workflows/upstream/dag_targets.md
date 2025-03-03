# Dag Targets

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-targets.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    with Workflow(
        generate_name="dag-target-",
        entrypoint="dag-target",
        arguments=Parameter(name="target", value="E"),
    ) as w:
        echo = Container(
            name="echo",
            inputs=Parameter(name="message"),
            image="alpine:3.7",
            command=["echo", "{{inputs.parameters.message}}"],
        )

        with DAG(
            name="dag-target",
            target="{{workflow.parameters.target}}",
        ):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "B"})
            C = echo(name="C", arguments={"message": "C"})
            D = echo(name="D", arguments={"message": "D"})
            E = echo(name="E", arguments={"message": "E"})

            A >> B >> D
            A >> C >> D
            C >> E
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-target-
    spec:
      entrypoint: dag-target
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
      - name: dag-target
        dag:
          target: '{{workflow.parameters.target}}'
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
          - name: E
            depends: C
            template: echo
            arguments:
              parameters:
              - name: message
                value: E
      arguments:
        parameters:
        - name: target
          value: E
    ```

