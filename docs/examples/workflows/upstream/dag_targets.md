# Dag Targets

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-targets.yaml).




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
      arguments:
        parameters:
        - name: target
          value: E
      entrypoint: dag-target
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
          target: '{{workflow.parameters.target}}'
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
          - arguments:
              parameters:
              - name: message
                value: E
            depends: C
            name: E
            template: echo
        name: dag-target
    ```

