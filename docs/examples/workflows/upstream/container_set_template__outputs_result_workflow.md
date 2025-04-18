# Container Set Template  Outputs Result Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/container-set-template/outputs-result-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.expr import g
    from hera.workflows import (
        DAG,
        ContainerNode,
        ContainerSet,
        Parameter,
        Script,
        Task,
        Workflow,
        models as m,
    )


    def _check():
        assert "{{inputs.parameters.x}}" == "hi"


    with Workflow(
        generate_name="outputs-result-",
        entrypoint="main",
    ) as w:
        with ContainerSet(name="group") as group:
            ContainerNode(name="main", image="python:alpine3.6", command=["python", "-c"], args=['print("hi")\n'])

        verify = Script(
            source=_check,
            image="python:alpine3.6",
            command=["python"],
            inputs=[Parameter(name="x")],
            add_cwd_to_sys_path=False,
            name="verify",
        )
        with DAG(name="main") as dag:
            a = Task(name="a", template=group)
            b = Task(
                name="b",
                arguments=m.Arguments(parameters=[m.Parameter(name="x", value=f"{g.tasks.a.outputs.result:$}")]),
                template=verify,
                dependencies=["a"],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: outputs-result-
    spec:
      entrypoint: main
      templates:
      - name: group
        containerSet:
          containers:
          - name: main
            image: python:alpine3.6
            args:
            - |
              print("hi")
            command:
            - python
            - -c
      - name: verify
        inputs:
          parameters:
          - name: x
        script:
          image: python:alpine3.6
          source: assert '{{inputs.parameters.x}}' == 'hi'
          command:
          - python
      - name: main
        dag:
          tasks:
          - name: a
            template: group
          - name: b
            template: verify
            dependencies:
            - a
            arguments:
              parameters:
              - name: x
                value: '{{tasks.a.outputs.result}}'
    ```

