# Dag With Param Passing






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Parameter, Task, Workflow

    with Workflow(generate_name="param-passing-", entrypoint="d") as w:
        out = Container(
            name="out",
            image="docker/whalesay:latest",
            command=["cowsay"],
            outputs=Parameter(name="x", value=42),
        )
        in_ = Container(
            name="in",
            image="docker/whalesay:latest",
            command=["cowsay"],
            args=["{{inputs.parameters.a}}"],
            inputs=Parameter(name="a"),
        )
        with DAG(name="d"):
            t1 = Task(name="a", template=out)
            t2 = Task(name="b", template=in_, arguments=t1.get_parameter("x").with_name("a"))
            t1 >> t2
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: param-passing-
    spec:
      entrypoint: d
      templates:
      - container:
          command:
          - cowsay
          image: docker/whalesay:latest
        name: out
        outputs:
          parameters:
          - name: x
            value: '42'
      - container:
          args:
          - '{{inputs.parameters.a}}'
          command:
          - cowsay
          image: docker/whalesay:latest
        inputs:
          parameters:
          - name: a
        name: in
      - dag:
          tasks:
          - name: a
            template: out
          - arguments:
              parameters:
              - name: a
                value: '{{tasks.a.outputs.parameters.x}}'
            depends: a
            name: b
            template: in
        name: d
    ```

