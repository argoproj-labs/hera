# Passing Parameters Between Tasks



This example shows how to pass parameters between tasks.


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
            t2 = Task(name="b", template=in_, arguments={"a": t1.get_parameter("x")})
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
      - name: out
        container:
          image: docker/whalesay:latest
          command:
          - cowsay
        outputs:
          parameters:
          - name: x
            value: '42'
      - name: in
        container:
          image: docker/whalesay:latest
          args:
          - '{{inputs.parameters.a}}'
          command:
          - cowsay
        inputs:
          parameters:
          - name: a
      - name: d
        dag:
          tasks:
          - name: a
            template: out
          - name: b
            depends: a
            template: in
            arguments:
              parameters:
              - name: a
                value: '{{tasks.a.outputs.parameters.x}}'
    ```

