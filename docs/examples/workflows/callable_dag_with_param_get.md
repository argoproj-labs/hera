# Callable Dag With Param Get






=== "Hera"

    ```python linenums="1"
    from typing_extensions import Annotated

    from hera.workflows import DAG, Parameter, Workflow, script


    @script(constructor="runner")
    def hello_with_output(name: str) -> Annotated[str, Parameter(name="output-message")]:
        return "Hello, {name}!".format(name=name)


    with Workflow(
        generate_name="callable-dag-",
        entrypoint="calling-dag",
    ) as w:
        with DAG(
            name="my-dag-with-outputs",
            inputs=Parameter(name="my-dag-input"),
            outputs=Parameter(
                name="my-dag-output",
                value_from={
                    "parameter": "{{hello.outputs.parameters.output-message}}"
                },  # Don't think we can improve this?
            ),
        ) as my_dag:
            hello_with_output(name="hello", arguments={"name": f"hello {my_dag.get_parameter('my-dag-input')}"})

        with DAG(name="calling-dag") as d:
            t1 = my_dag(name="call-1", arguments={"my-dag-input": "call-1"})
            # Here, t1 is a Task from the called dag, so get_parameter is called on the Task to get the output parameter! 🚀
            t2 = my_dag(name="call-2", arguments=t1.get_parameter("my-dag-output").with_name("my-dag-input"))
            t1 >> t2
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: callable-dag-
    spec:
      entrypoint: calling-dag
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: name
                value: hello {{inputs.parameters.my-dag-input}}
            name: hello
            template: hello-with-output
        inputs:
          parameters:
          - name: my-dag-input
        name: my-dag-with-outputs
        outputs:
          parameters:
          - name: my-dag-output
            valueFrom:
              parameter: '{{hello.outputs.parameters.output-message}}'
      - inputs:
          parameters:
          - name: name
        name: hello-with-output
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.callable_dag_with_param_get:hello_with_output
          command:
          - python
          image: python:3.8
          source: '{{inputs.parameters}}'
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: my-dag-input
                value: call-1
            name: call-1
            template: my-dag-with-outputs
          - arguments:
              parameters:
              - name: my-dag-input
                value: '{{tasks.call-1.outputs.parameters.my-dag-output}}'
            depends: call-1
            name: call-2
            template: my-dag-with-outputs
        name: calling-dag
    ```

