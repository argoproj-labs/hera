# Dag Task Level Timeout

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/dag-task-level-timeout.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Workflow

    with Workflow(
        generate_name="dag-task-level-timeout-",
        entrypoint="diamond",
    ) as w:
        echo = Container(
            name="echo",
            timeout="{{inputs.parameters.timeout}}",
            image="alpine:3.7",
            command=["sleep", "15s"],
            inputs=Parameter(name="timeout"),
        )
        with DAG(name="diamond"):
            a = echo(name="A", arguments={"timeout": "20s"})
            b = echo(name="B", arguments={"timeout": "10s"})
            c = echo(name="C", arguments={"timeout": "20s"})
            a >> [b, c]
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-task-level-timeout-
    spec:
      entrypoint: diamond
      templates:
      - container:
          command:
          - sleep
          - 15s
          image: alpine:3.7
        inputs:
          parameters:
          - name: timeout
        name: echo
        timeout: '{{inputs.parameters.timeout}}'
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: timeout
                value: 20s
            name: A
            template: echo
          - arguments:
              parameters:
              - name: timeout
                value: 10s
            depends: A
            name: B
            template: echo
          - arguments:
              parameters:
              - name: timeout
                value: 20s
            depends: A
            name: C
            template: echo
        name: diamond
    ```

