# Parameter Aggregation Dag

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/parameter-aggregation-dag.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, Task, Workflow
    from hera.workflows.models import Arguments, Inputs, Item, Outputs, Parameter, ValueFrom

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="parameter-aggregation-dag-",
        entrypoint="parameter-aggregation",
    ) as w:
        with DAG(
            name="parameter-aggregation",
        ) as invocator:
            Task(
                with_items=[
                    Item(
                        root=1,
                    ),
                    Item(
                        root=2,
                    ),
                    Item(
                        root=3,
                    ),
                    Item(
                        root=4,
                    ),
                ],
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="num",
                            value="{{item}}",
                        )
                    ],
                ),
                name="odd-or-even",
                template="odd-or-even",
            )
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="{{tasks.odd-or-even.outputs.parameters.num}}",
                        )
                    ],
                ),
                name="print-nums",
                template="print-message",
                depends="odd-or-even",
            )
            Task(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="{{tasks.odd-or-even.outputs.parameters.evenness}}",
                        )
                    ],
                ),
                name="print-evenness",
                template="print-message",
                depends="odd-or-even",
            )
            Task(
                with_param="{{tasks.odd-or-even.outputs.parameters}}",
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="num",
                            value="{{item.num}}",
                        )
                    ],
                ),
                name="divide-by-2",
                template="divide-by-2",
                when="{{item.evenness}} == even",
                depends="odd-or-even",
            )
            Task(
                with_param="{{tasks.divide-by-2.outputs.result}}",
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="message",
                            value="{{item}}",
                        )
                    ],
                ),
                name="print",
                template="print-message",
                depends="divide-by-2",
            )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="num",
                    )
                ],
            ),
            name="odd-or-even",
            outputs=Outputs(
                parameters=[
                    Parameter(
                        name="num",
                        value_from=ValueFrom(
                            path="/tmp/num",
                        ),
                    ),
                    Parameter(
                        name="evenness",
                        value_from=ValueFrom(
                            path="/tmp/even",
                        ),
                    ),
                ],
            ),
            args=[
                'sleep 1 &&\necho {{inputs.parameters.num}} > /tmp/num &&\nif [ $(({{inputs.parameters.num}}%2)) -eq 0 ]; then\n  echo "even" > /tmp/even;\nelse\n  echo "odd" > /tmp/even;\nfi\n'
            ],
            command=["sh", "-c"],
            image="alpine:latest",
        )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="num",
                    )
                ],
            ),
            name="divide-by-2",
            args=["echo $(({{inputs.parameters.num}}/2))"],
            command=["sh", "-c"],
            image="alpine:latest",
        )
        Container(
            inputs=Inputs(
                parameters=[
                    Parameter(
                        name="message",
                    )
                ],
            ),
            name="print-message",
            args=["{{inputs.parameters.message}}"],
            command=["echo"],
            image="busybox",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: parameter-aggregation-dag-
    spec:
      entrypoint: parameter-aggregation
      templates:
      - name: parameter-aggregation
        dag:
          tasks:
          - name: odd-or-even
            template: odd-or-even
            withItems:
            - 1
            - 2
            - 3
            - 4
            arguments:
              parameters:
              - name: num
                value: '{{item}}'
          - name: print-nums
            depends: odd-or-even
            template: print-message
            arguments:
              parameters:
              - name: message
                value: '{{tasks.odd-or-even.outputs.parameters.num}}'
          - name: print-evenness
            depends: odd-or-even
            template: print-message
            arguments:
              parameters:
              - name: message
                value: '{{tasks.odd-or-even.outputs.parameters.evenness}}'
          - name: divide-by-2
            depends: odd-or-even
            template: divide-by-2
            when: '{{item.evenness}} == even'
            withParam: '{{tasks.odd-or-even.outputs.parameters}}'
            arguments:
              parameters:
              - name: num
                value: '{{item.num}}'
          - name: print
            depends: divide-by-2
            template: print-message
            withParam: '{{tasks.divide-by-2.outputs.result}}'
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
      - name: odd-or-even
        container:
          image: alpine:latest
          args:
          - |
            sleep 1 &&
            echo {{inputs.parameters.num}} > /tmp/num &&
            if [ $(({{inputs.parameters.num}}%2)) -eq 0 ]; then
              echo "even" > /tmp/even;
            else
              echo "odd" > /tmp/even;
            fi
          command:
          - sh
          - -c
        inputs:
          parameters:
          - name: num
        outputs:
          parameters:
          - name: num
            valueFrom:
              path: /tmp/num
          - name: evenness
            valueFrom:
              path: /tmp/even
      - name: divide-by-2
        container:
          image: alpine:latest
          args:
          - echo $(({{inputs.parameters.num}}/2))
          command:
          - sh
          - -c
        inputs:
          parameters:
          - name: num
      - name: print-message
        container:
          image: busybox
          args:
          - '{{inputs.parameters.message}}'
          command:
          - echo
        inputs:
          parameters:
          - name: message
    ```

