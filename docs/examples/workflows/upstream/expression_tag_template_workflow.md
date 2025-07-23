# Expression Tag Template Workflow

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/expression-tag-template-workflow.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Task, Workflow
    from hera.workflows.models import Arguments, Inputs, Outputs, Parameter, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        annotations={"workflows.argoproj.io/version": ">= 3.1.0"},
        generate_name="expression-tag-template-",
        labels={"workflows.argoproj.io/test": "true"},
        entrypoint="main",
    ) as w:
        with DAG(
            name="main",
        ) as invocator:
            Task(
                with_param="{{=toJson(filter([1, 3], {# > 1}))}}",
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="foo",
                            value="{{=item}}",
                        )
                    ],
                ),
                name="task-0",
                template="pod-0",
            )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="foo",
                    )
                ],
            ),
            name="pod-0",
            outputs=Outputs(
                parameters=[
                    Parameter(
                        name="output",
                        value_from=ValueFrom(
                            path="/output",
                        ),
                    )
                ],
            ),
            args=[
                "echo",
                "hello {{=asInt(inputs.parameters.foo) * 10}} @ {{=sprig.date('2006', workflow.creationTimestamp)}}\n",
                "/output",
            ],
            image="argoproj/argosay:v2",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: expression-tag-template-
      annotations:
        workflows.argoproj.io/version: '>= 3.1.0'
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: main
        dag:
          tasks:
          - name: task-0
            template: pod-0
            withParam: '{{=toJson(filter([1, 3], {# > 1}))}}'
            arguments:
              parameters:
              - name: foo
                value: '{{=item}}'
      - name: pod-0
        container:
          image: argoproj/argosay:v2
          args:
          - echo
          - |
            hello {{=asInt(inputs.parameters.foo) * 10}} @ {{=sprig.date('2006', workflow.creationTimestamp)}}
          - /output
        inputs:
          parameters:
          - name: foo
        outputs:
          parameters:
          - name: output
            valueFrom:
              path: /output
    ```

